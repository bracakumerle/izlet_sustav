'use strict';
const https = require('https');

const ARTIST_ID  = '6610944';
const LABEL_ID   = '4368922';
const USER_AGENT = 'izlet_sustav/1.0 bracakumerle@gmail.com';

function get(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': USER_AGENT } }, (res) => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        try   { resolve({ status: res.statusCode, data: JSON.parse(Buffer.concat(chunks).toString()) }); }
        catch { resolve({ status: res.statusCode, data: {} }); }
      });
    }).on('error', reject);
  });
}

exports.handler = async () => {
  const headers = {
    'Content-Type':                'application/json',
    'Access-Control-Allow-Origin': '*',
    'Cache-Control':               'public, max-age=3600',
  };

  try {
    const [artistRes, releasesRes, labelRes] = await Promise.all([
      get(`https://api.discogs.com/artists/${ARTIST_ID}`),
      get(`https://api.discogs.com/artists/${ARTIST_ID}/releases?sort=year&sort_order=desc&per_page=10&page=1`),
      get(`https://api.discogs.com/labels/${LABEL_ID}`),
    ]);

    const artist   = artistRes.data;
    const label    = labelRes.data;
    const releases = (releasesRes.data.releases || []).map(r => ({
      id:    r.id,
      title: r.title,
      year:  r.year,
      type:  r.type,
      role:  r.role,
      thumb: r.thumb,
      url:   `https://www.discogs.com${r.resource_url?.replace('https://api.discogs.com', '') || ''}`,
    }));

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        fetched_at: new Date().toISOString(),
        artist: {
          id:           artist.id,
          name:         artist.name,
          profile:      (artist.profile || '').slice(0, 500),
          urls:         (artist.urls || []).slice(0, 5),
          images:       (artist.images || []).slice(0, 2).map(i => i.uri),
          data_quality: artist.data_quality,
          discogs_url:  `https://www.discogs.com/artist/${ARTIST_ID}`,
        },
        releases,
        label: {
          id:          label.id,
          name:        label.name,
          profile:     (label.profile || '').slice(0, 300),
          discogs_url: `https://www.discogs.com/label/${LABEL_ID}`,
        },
        pagination: {
          total_releases: releasesRes.data.pagination?.items || releases.length,
        },
      }, null, 2),
    };
  } catch (err) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: err.message }) };
  }
};

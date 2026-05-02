'use strict';
const https = require('https');

const ARTIST_ID = '11wCFDSyZy0LfWkgllak6d';

// Module-level token cache (survives warm Lambda invocations)
let cachedToken  = null;
let tokenExpiry  = 0;

function request(options, body = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        const raw = Buffer.concat(chunks).toString();
        try   { resolve({ status: res.statusCode, data: JSON.parse(raw) }); }
        catch { resolve({ status: res.statusCode, data: raw }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function getToken() {
  if (cachedToken && Date.now() < tokenExpiry) return cachedToken;

  const { SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET } = process.env;
  if (!SPOTIFY_CLIENT_ID || !SPOTIFY_CLIENT_SECRET) {
    throw new Error('Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET env vars');
  }

  const creds = Buffer.from(`${SPOTIFY_CLIENT_ID}:${SPOTIFY_CLIENT_SECRET}`).toString('base64');
  const body  = 'grant_type=client_credentials';

  const { data } = await request({
    hostname: 'accounts.spotify.com',
    path:     '/api/token',
    method:   'POST',
    headers: {
      'Authorization':  `Basic ${creds}`,
      'Content-Type':   'application/x-www-form-urlencoded',
      'Content-Length': Buffer.byteLength(body),
    },
  }, body);

  if (!data.access_token) throw new Error(`Token error: ${JSON.stringify(data)}`);

  cachedToken = data.access_token;
  tokenExpiry = Date.now() + (data.expires_in - 60) * 1000;
  return cachedToken;
}

async function spotifyGet(path, token) {
  const { data, status } = await request({
    hostname: 'api.spotify.com',
    path,
    method:  'GET',
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return { data, status };
}

exports.handler = async () => {
  const headers = {
    'Content-Type':                'application/json',
    'Access-Control-Allow-Origin': '*',
    'Cache-Control':               'public, max-age=300',
  };

  try {
    const token = await getToken();

    const [artistRes, tracksRes, albumsRes] = await Promise.all([
      spotifyGet(`/v1/artists/${ARTIST_ID}`, token),
      spotifyGet(`/v1/artists/${ARTIST_ID}/top-tracks?market=HR`, token),
      spotifyGet(`/v1/artists/${ARTIST_ID}/albums?include_groups=album,single&market=HR&limit=20`, token),
    ]);

    const artist     = artistRes.data;
    const top_tracks = (tracksRes.data.tracks || []).map(t => ({
      id:         t.id,
      name:       t.name,
      duration_ms: t.duration_ms,
      popularity: t.popularity,
      preview_url: t.preview_url,
      external_url: t.external_urls?.spotify,
      album: {
        name:          t.album?.name,
        release_date:  t.album?.release_date,
        image:         t.album?.images?.[1]?.url,
      },
    }));
    const albums = (albumsRes.data.items || []).map(a => ({
      id:           a.id,
      name:         a.name,
      type:         a.album_type,
      release_date: a.release_date,
      total_tracks: a.total_tracks,
      image:        a.images?.[1]?.url,
      external_url: a.external_urls?.spotify,
    }));

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        fetched_at:  new Date().toISOString(),
        artist: {
          id:          artist.id,
          name:        artist.name,
          followers:   artist.followers?.total,
          popularity:  artist.popularity,
          genres:      artist.genres,
          image:       artist.images?.[0]?.url,
          external_url: artist.external_urls?.spotify,
        },
        top_tracks,
        albums,
      }, null, 2),
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message }),
    };
  }
};

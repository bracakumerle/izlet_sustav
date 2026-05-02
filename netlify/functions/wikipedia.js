'use strict';
const https = require('https');

const ARTICLE    = 'IZLET';
const LANG       = 'hr';
const WIKIDATA_ID = 'Q139595518';
const USER_AGENT  = 'izlet_sustav/1.0 (bracakumerle@gmail.com)';

function get(url, extraHeaders = {}) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': USER_AGENT, ...extraHeaders } }, (res) => {
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
    const [wikiRes, wdRes] = await Promise.all([
      get(`https://${LANG}.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(ARTICLE)}`),
      get(`https://www.wikidata.org/w/api.php?action=wbgetentities&ids=${WIKIDATA_ID}&languages=hr%7Cen&props=labels%7Cdescriptions%7Cclaims&format=json`),
    ]);

    const wiki   = wikiRes.data;
    const entity = wdRes.data.entities?.[WIKIDATA_ID] || {};
    const claims = entity.claims || {};

    const claim_val = (pid) => {
      const c = (claims[pid] || [])[0];
      return c?.mainsnak?.datavalue?.value;
    };

    const spotify_id = claim_val('P1902');
    const mb_id      = claim_val('P434');
    const yt_channel = claim_val('P2397');
    const inception  = claim_val('P571');
    const website    = claim_val('P856');

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        fetched_at: new Date().toISOString(),
        wikipedia: {
          title:       wiki.title,
          description: wiki.description,
          extract:     wiki.extract,
          thumbnail:   wiki.thumbnail?.source,
          last_edited: wiki.timestamp,
          url:         wiki.content_urls?.desktop?.page,
          wikidata_id: wiki.wikibase_item,
          found:       wikiRes.status === 200,
        },
        wikidata: {
          qid:         WIKIDATA_ID,
          label_hr:    entity.labels?.hr?.value,
          label_en:    entity.labels?.en?.value,
          desc_hr:     entity.descriptions?.hr?.value,
          desc_en:     entity.descriptions?.en?.value,
          spotify_id:  typeof spotify_id === 'string' ? spotify_id : null,
          mb_id:       typeof mb_id      === 'string' ? mb_id      : null,
          yt_channel:  typeof yt_channel === 'string' ? yt_channel : null,
          founded:     typeof inception  === 'string' ? inception.replace(/^\+(\d{4}).*/, '$1') : null,
          website:     typeof website    === 'string' ? website    : null,
          url:         `https://www.wikidata.org/wiki/${WIKIDATA_ID}`,
        },
      }, null, 2),
    };
  } catch (err) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: err.message }) };
  }
};

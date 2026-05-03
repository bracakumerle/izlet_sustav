'use strict';
const https = require('https');

const PAGE_ID    = '142089129226973';
const GRAPH_BASE = 'https://graph.facebook.com/v19.0';
const PAGE_FIELDS = 'name,fan_count,followers_count,about,website,verification_status,picture.type(large)';
const POST_FIELDS = 'id,message,story,created_time';

function get(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        try   { resolve({ status: res.statusCode, data: JSON.parse(Buffer.concat(chunks).toString()) }); }
        catch { resolve({ status: res.statusCode, data: {} }); }
      });
    }).on('error', reject);
  });
}

async function exchangePageToken(userToken) {
  const enc = encodeURIComponent;
  const res = await get(
    `${GRAPH_BASE}/${PAGE_ID}?fields=access_token&access_token=${enc(userToken)}`
  );
  return res.data.access_token || userToken;
}

exports.handler = async () => {
  const headers = {
    'Content-Type':                'application/json',
    'Access-Control-Allow-Origin': '*',
    'Cache-Control':               'public, max-age=300',
  };

  const rawToken = process.env.FACEBOOK_PAGE_TOKEN;
  if (!rawToken) {
    return {
      statusCode: 503,
      headers,
      body: JSON.stringify({ error: 'FACEBOOK_PAGE_TOKEN not configured', page_id: PAGE_ID }),
    };
  }

  try {
    const enc   = encodeURIComponent;
    const token = await exchangePageToken(rawToken);

    const [pageRes, postsRes] = await Promise.all([
      get(`${GRAPH_BASE}/${PAGE_ID}?fields=${enc(PAGE_FIELDS)}&access_token=${enc(token)}`),
      get(`${GRAPH_BASE}/${PAGE_ID}/posts?fields=${enc(POST_FIELDS)}&limit=6&access_token=${enc(token)}`),
    ]);

    const page  = pageRes.data;
    const posts = (postsRes.data.data || []).map(p => ({
      id:           p.id,
      message:      p.message || p.story || null,
      created_time: p.created_time,
    }));

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        fetched_at:      new Date().toISOString(),
        page: {
          id:              page.id,
          name:            page.name,
          fan_count:       page.fan_count,
          followers_count: page.followers_count,
          about:           page.about || null,
          website:         page.website || null,
          verified:        page.verification_status === 'blue_verified',
          picture_url:     page.picture?.data?.url || null,
        },
        latest_posts: posts,
      }, null, 2),
    };
  } catch (err) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: err.message }) };
  }
};

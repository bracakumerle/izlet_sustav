'use strict';
const https = require('https');

const CHANNEL_ID = 'UC8jNEBUrOqCcXqVleV9ccKg';

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

exports.handler = async () => {
  const headers = {
    'Content-Type':                'application/json',
    'Access-Control-Allow-Origin': '*',
    'Cache-Control':               'public, max-age=600',
  };

  const key = process.env.YOUTUBE_API_KEY;
  if (!key) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Missing YOUTUBE_API_KEY' }) };
  }

  try {
    const [channelRes, videosRes] = await Promise.all([
      get(`https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id=${CHANNEL_ID}&key=${key}`),
      get(`https://www.googleapis.com/youtube/v3/search?channelId=${CHANNEL_ID}&type=video&order=date&maxResults=6&part=snippet&key=${key}`),
    ]);

    const channel = channelRes.data.items?.[0] || {};
    const stats   = channel.statistics || {};
    const snippet = channel.snippet    || {};

    const latest_videos = (videosRes.data.items || []).map(v => ({
      video_id:     v.id.videoId,
      title:        v.snippet.title,
      published_at: v.snippet.publishedAt,
      thumbnail:    v.snippet.thumbnails?.medium?.url,
      url:          `https://www.youtube.com/watch?v=${v.id.videoId}`,
    }));

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        fetched_at:       new Date().toISOString(),
        channel_id:       CHANNEL_ID,
        channel_name:     snippet.title,
        channel_url:      `https://www.youtube.com/@bracakumerle`,
        subscriber_count: parseInt(stats.subscriberCount || 0),
        view_count:       parseInt(stats.viewCount       || 0),
        video_count:      parseInt(stats.videoCount      || 0),
        thumbnail:        snippet.thumbnails?.default?.url,
        latest_videos,
      }, null, 2),
    };
  } catch (err) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: err.message }) };
  }
};

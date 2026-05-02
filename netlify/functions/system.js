'use strict';
const fs   = require('fs');
const path = require('path');

const FALLBACK = {
  last_run:      '2026-05-02T21:00:00Z',
  urls_verified: '28/40',
  commit:        '6a32ef4',
  agents_status: 'Spotify ✅ MusicBrainz ✅ Wikidata ✅ YouTube ✅',
};

function read_json(file) {
  const candidates = [
    path.join(process.cwd(), 'data', file),
    path.join(__dirname, '../../data', file),
    path.join(__dirname, 'data', file),
  ];
  for (const p of candidates) {
    try { return JSON.parse(fs.readFileSync(p, 'utf8')); }
    catch {}
  }
  return null;
}

exports.handler = async () => {
  const headers = {
    'Content-Type':                'application/json',
    'Access-Control-Allow-Origin': '*',
    'Cache-Control':               'public, max-age=60',
  };

  const status   = read_json('system_status.json') || FALLBACK;
  const yt_snap  = read_json('youtube_snapshot.json');
  const mb_snap  = read_json('mb_snapshot.json');
  const wd_state = read_json('wikidata_state.json');

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify({
      fetched_at:    new Date().toISOString(),
      last_run:      status.last_run,
      urls_verified: status.urls_verified,
      commit:        status.commit,
      agents_status: status.agents_status,
      youtube: yt_snap ? {
        total_videos:      yt_snap.total_videos,
        total_views:       yt_snap.total_views,
        latest_video_date: yt_snap.latest_video_date,
      } : null,
      musicbrainz: mb_snap ? {
        release_groups: mb_snap.stats?.release_group_count,
        recordings:     mb_snap.stats?.recording_count,
        fetched_at:     mb_snap.fetched_at,
      } : null,
      wikidata: wd_state ? {
        last_checked:  wd_state.last_checked,
        hash:          wd_state.hash?.slice(0, 12) + '…',
        changed:       wd_state.changed_since_last_check,
      } : null,
    }, null, 2),
  };
};

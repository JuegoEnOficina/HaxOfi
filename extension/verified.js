// HaxOfi verified rooms on haxball.com: a blue check beside every room its community registered with HaxOfi
// (GET https://api.haxofi.com/rooms/verified, the list the HaxOfi app reads).
//
// The room list rows carry no room id, so this script reads the list the game itself downloads (/rs/api/list,
// wrapped below) and matches each row by what it shows: name, players, password and flag. An impostor copies a
// community's room name to grab the IP of the players who join, so a row gets the check only when EVERY listed
// room showing those same values is verified by the same community. A copy that cannot be told apart leaves both
// rows without the check: never a check on a fake.
//
// Runs in the page (manifest "world": "MAIN") at document_start, before the game's first list request.
(() => {
  const VERIFIED_URL = 'https://api.haxofi.com/rooms/verified';
  const VERIFIED_MAX_AGE_MS = 60_000;
  const BADGE_CLASS = 'haxofi-verified';

  // HaxBall writes text one UTF-16 unit at a time (CESU-8): an emoji is two 3-byte surrogates, which TextDecoder
  // turns into U+FFFD. Decode each sequence to its unit and let the string pair the surrogates back up.
  function decodeText(bytes) {
    let out = '';
    for (let i = 0; i < bytes.length;) {
      const lead = bytes[i];
      if (lead < 0x80) {
        out += String.fromCharCode(lead);
        i += 1;
      } else if (lead < 0xe0) {
        out += String.fromCharCode(((lead & 0x1f) << 6) | (bytes[i + 1] & 0x3f));
        i += 2;
      } else if (lead < 0xf0) {
        out += String.fromCharCode(((lead & 0x0f) << 12) | ((bytes[i + 1] & 0x3f) << 6) | (bytes[i + 2] & 0x3f));
        i += 3;
      } else {
        out += String.fromCodePoint(((lead & 0x07) << 18) | ((bytes[i + 1] & 0x3f) << 12)
          | ((bytes[i + 2] & 0x3f) << 6) | (bytes[i + 3] & 0x3f));
        i += 4;
      }
    }
    return out;
  }

  // /rs/api/list: one version byte, then per room a u16 (big endian) length + id and a u16 length + data block.
  // The data block, little endian: u16 version, name and flag (varint length + text), lat and lon (f32),
  // password (u8), max players (u8), players (u8). A block that does not read cleanly drops only its room.
  function parseRoomList(buffer) {
    const view = new DataView(buffer);
    const rooms = [];
    let at = 1;
    while (at + 2 <= view.byteLength) {
      const idLength = view.getUint16(at);
      const id = decodeText(new Uint8Array(buffer, at + 2, Math.min(idLength, view.byteLength - at - 2)));
      at += 2 + idLength;
      if (at + 2 > view.byteLength) break;
      const dataEnd = at + 2 + view.getUint16(at);
      if (dataEnd > view.byteLength) break;
      const room = readRoomData(view, at + 2, dataEnd);
      if (room) rooms.push(Object.assign({ id }, room));
      at = dataEnd;
    }
    return rooms;
  }

  function readRoomData(view, start, end) {
    let at = start + 2;
    function varint() {
      let value = 0;
      for (let shift = 0; shift < 35; shift += 7) {
        if (at >= end) throw new RangeError('room data ends inside a varint');
        const byte = view.getUint8(at++);
        value |= (byte & 0x7f) << shift;
        if (!(byte & 0x80)) return value;
      }
      throw new RangeError('varint too long');
    }
    function text() {
      const length = varint();
      if (at + length > end) throw new RangeError('room data ends inside a string');
      const value = decodeText(new Uint8Array(view.buffer, at, length));
      at += length;
      return value;
    }
    try {
      const name = text();
      const flag = text();
      at += 8;   // lat, lon
      if (at + 3 > end) return null;
      const locked = view.getUint8(at) !== 0;
      const maxPlayers = view.getUint8(at + 1);
      const players = view.getUint8(at + 2);
      return { name, flag: flag.toLowerCase(), locked, maxPlayers, players };
    } catch (e) {
      return null;
    }
  }

  // The values a row shows, in the order rowKey reads them off the DOM.
  function roomKey(name, players, maxPlayers, locked, flag) {
    return [name, players + '/' + maxPlayers, locked ? 'Yes' : 'No', flag].join('\n');
  }

  // key -> ids of every listed room that shows exactly that row.
  function indexRooms(rooms) {
    const byKey = new Map();
    for (const room of rooms) {
      const key = roomKey(room.name, room.players, room.maxPlayers, room.locked, room.flag);
      if (!byKey.has(key)) byKey.set(key, []);
      byKey.get(key).push(room.id);
    }
    return byKey;
  }

  // The community that verified every room behind the row, or null (unknown row, an unverified twin, two
  // communities).
  function communityOf(ids, communityById) {
    if (!ids || !ids.length) return null;
    const community = communityById[ids[0]];
    return community && ids.every((id) => communityById[id] === community) ? community : null;
  }

  if (typeof window === 'undefined') {
    module.exports = { decodeText, parseRoomList, roomKey, indexRooms, communityOf };
    return;
  }

  let roomsByKey = new Map();
  let communityById = {};
  let verifiedAt = 0;
  let verifiedLoading = false;
  let markQueued = false;

  function refreshVerified() {
    if (verifiedLoading || Date.now() - verifiedAt < VERIFIED_MAX_AGE_MS) return;
    verifiedLoading = true;
    fetch(VERIFIED_URL)
      .then((res) => (res.ok ? res.json() : null))
      .then((body) => {
        if (body && body.names && typeof body.names === 'object') {
          communityById = body.names;
          verifiedAt = Date.now();
          queueMark();
        }
      })
      .catch(() => {})
      .finally(() => { verifiedLoading = false; });
  }

  const open = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url) {
    if (/\/rs\/api\/list(?:[?#]|$)/.test(String(url))) {
      this.addEventListener('load', () => {
        try {
          if (this.status !== 200 || !(this.response instanceof ArrayBuffer)) return;
          roomsByKey = indexRooms(parseRoomList(this.response));
          refreshVerified();
          queueMark();
        } catch (e) {
          roomsByKey = new Map();
        }
      });
    }
    return open.apply(this, arguments);
  };

  function rowKey(row) {
    const name = row.querySelector('[data-hook="name"]');
    const players = row.querySelector('[data-hook="players"]');
    const pass = row.querySelector('[data-hook="pass"]');
    const flag = row.querySelector('[data-hook="flag"]');
    if (!name || !players || !pass || !flag) return null;
    const country = /\bf-([a-z0-9]+)\b/i.exec(flag.className);
    return [name.textContent, players.textContent.trim(), pass.textContent.trim(), country ? country[1].toLowerCase() : ''].join('\n');
  }

  function badge(community) {
    const mark = document.createElement('span');
    mark.className = BADGE_CLASS;
    mark.title = 'Verificada por ' + community;
    mark.style.cssText = 'display:inline-block;width:13px;height:13px;margin-right:4px;vertical-align:-2px';
    mark.innerHTML = '<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true">'
      + '<circle cx="12" cy="12" r="12" fill="#3D7BFF"/>'
      + '<path d="M6.5 12.5l3.5 3.5 7.5-8" fill="none" stroke="#fff" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    return mark;
  }

  // Idempotent: a row already showing the right badge is left alone, so the observer's own echo ends here.
  function mark() {
    markQueued = false;
    const rows = document.querySelectorAll('tbody[data-hook="list"] > tr');
    for (const row of rows) {
      const nameHook = row.querySelector('[data-hook="name"]');
      if (!nameHook) continue;
      const key = rowKey(row);
      const community = key ? communityOf(roomsByKey.get(key), communityById) : null;
      const current = row.querySelector('.' + BADGE_CLASS);
      if (current && community && current.title === 'Verificada por ' + community) continue;
      if (current) current.remove();
      if (community) nameHook.before(badge(community));
    }
  }

  function queueMark() {
    if (markQueued) return;
    markQueued = true;
    setTimeout(mark, 0);   // not requestAnimationFrame: it never fires in a tab that is not painting
  }

  new MutationObserver(() => { if (roomsByKey.size) queueMark(); })
    .observe(document, { childList: true, subtree: true });
  refreshVerified();
})();

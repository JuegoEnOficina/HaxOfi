// node --test extension/
const { test } = require('node:test');
const assert = require('node:assert');
const { decodeText, parseRoomList, roomKey, indexRooms, communityOf } = require('./verified.js');

// CESU-8, as HaxBall writes it: each UTF-16 unit on its own, so an emoji is two 3-byte surrogates.
function cesu(text) {
  const bytes = [];
  for (let i = 0; i < text.length; i++) {
    const unit = text.charCodeAt(i);
    if (unit < 0x80) bytes.push(unit);
    else if (unit < 0x800) bytes.push(0xc0 | (unit >> 6), 0x80 | (unit & 0x3f));
    else bytes.push(0xe0 | (unit >> 12), 0x80 | ((unit >> 6) & 0x3f), 0x80 | (unit & 0x3f));
  }
  return bytes;
}

function listBody(rooms) {
  const out = [0];
  for (const room of rooms) {
    const id = cesu(room.id);
    const name = cesu(room.name);
    const flag = cesu(room.flag);
    const data = [9, 0];
    for (let length = name.length; ; length >>= 7) {   // varint
      if (length < 0x80) { data.push(length); break; }
      data.push((length & 0x7f) | 0x80);
    }
    data.push(...name, flag.length, ...flag, 0, 0, 0, 0, 0, 0, 0, 0, room.locked ? 1 : 0, room.maxPlayers, room.players);
    out.push(id.length >> 8, id.length & 0xff, ...id, data.length >> 8, data.length & 0xff, ...data);
  }
  return new Uint8Array(out).buffer;
}

const OFICINA = { id: 'aaaaaaaaaaa', name: '🛑 ❰𝗢𝗙𝗜𝗖𝗜𝗡𝗔❱ X3', flag: 'AR', locked: false, maxPlayers: 12, players: 5 };

test('reads every room, emoji names and names over 127 bytes included', () => {
  const long = Object.assign({}, OFICINA, { id: 'bbbbbbbbbbb', name: '𝗢'.repeat(30) });
  const rooms = parseRoomList(listBody([OFICINA, long]));
  assert.deepStrictEqual(rooms.map((r) => [r.id, r.name, r.flag, r.players, r.maxPlayers, r.locked]),
    [[OFICINA.id, OFICINA.name, 'ar', 5, 12, false], [long.id, long.name, 'ar', 5, 12, false]]);
  assert.strictEqual(decodeText(new Uint8Array(cesu('ñ⚽🦆'))), 'ñ⚽🦆');
});

test('a cut list keeps the rooms before the cut', () => {
  const body = listBody([OFICINA, Object.assign({}, OFICINA, { id: 'bbbbbbbbbbb' })]);
  assert.strictEqual(parseRoomList(body.slice(0, body.byteLength - 4)).length, 1);
});

test('a row is checked only when every room showing it is verified by one community', () => {
  const copy = Object.assign({}, OFICINA, { id: 'fakefakefak' });
  const verified = { [OFICINA.id]: 'Oficina' };
  const index = (rooms) => indexRooms(parseRoomList(listBody(rooms)));
  const key = roomKey(OFICINA.name, 5, 12, false, 'ar');
  assert.strictEqual(communityOf(index([OFICINA]).get(key), verified), 'Oficina');
  assert.strictEqual(communityOf(index([OFICINA, copy]).get(key), verified), null);
  assert.strictEqual(communityOf(index([OFICINA, copy]).get(key), Object.assign({ fakefakefak: 'Otra' }, verified)), null);
  assert.strictEqual(communityOf(index([copy]).get(key), verified), null);
  assert.strictEqual(communityOf(undefined, verified), null);
});

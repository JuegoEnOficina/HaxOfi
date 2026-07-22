# Chrome Web Store listing: HaxOfi Salas Verificadas

Upload `docs/verificadas/haxofi-salas-verificadas.zip` (built by `extension/pack.sh`).
Graphics in this folder: `screenshot-1.png` and `screenshot-2.png` (1280x800), `promo-tile.png` (440x280,
source `promo-tile.html`). The 128px icon comes from the zip.

## Store listing tab

**Name** (from the manifest)

HaxOfi Salas Verificadas

**Short description** (from the manifest, 132 characters max)

Muestra un check azul en las salas de HaxBall verificadas por su comunidad. Las copias que usan su nombre no lo tienen.

**Detailed description**

Hay salas que copian el nombre de una comunidad conocida para que entres pensando que es la oficial y sacarte la IP.

Con esta extensión, la lista de salas de haxball.com muestra un check azul al lado de cada sala verificada por su comunidad. Si pasás el mouse por el check, ves qué comunidad la verificó.

Las copias no tienen el check. Si una copia es idéntica a la sala original y no se pueden distinguir, ninguna de las dos lo muestra. El check nunca aparece en una sala falsa.

Las comunidades verifican sus salas con HaxOfi. Ya están Oficina, Sanguchito y Cuacki, y se suman más.

No hace falta cuenta ni configuración. Instalala, entrá a haxball.com/play y listo.

La extensión no lee ni guarda nada tuyo. Solo consulta la lista pública de salas verificadas de HaxOfi.

Más info: https://haxofi.com/verificadas/

**Category**: Fun (or Games, whichever the form offers)
**Language**: Spanish (Latin America)
**Homepage URL**: https://haxofi.com/verificadas/
**Support URL**: https://haxofi.com/ (or the HaxOfi Discord invite)

## Privacy practices tab

**Single purpose**

Mostrar un check azul en la lista de salas de haxball.com al lado de las salas verificadas por su comunidad, para que los jugadores distingan las salas oficiales de las copias.

**Permission justification: host access (content script on https://*.haxball.com/*game.html)**

La extensión necesita leer la lista de salas que muestra la página de juego de haxball.com para agregar el check al lado de cada sala verificada. Solo corre en esa página y no pide ningún otro permiso.

**Remote code**: No, I am not using remote code. (The extension downloads a JSON list of verified room ids
from https://api.haxofi.com/rooms/verified. That is data, not code.)

**Data usage**: collects nothing. Leave every data category unchecked, then tick the three certifications
(no selling to third parties, no unrelated use, no creditworthiness use).

**Privacy policy URL**: https://haxofi.com/verificadas/privacidad/ (its own policy page: the store rejected the
homepage on 2026-11-04, "Purple Nickel", owner sites are not a valid privacy policy).

## Distribution tab

Visibility: Public. Regions: all. Free.

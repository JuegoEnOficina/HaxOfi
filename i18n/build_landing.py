#!/usr/bin/env python3
"""Generate docs/pt/index.html and docs/en/index.html from the Spanish landing page docs/index.html.

Edit the Spanish page, add or update its strings in STRINGS, then run `python3 i18n/build_landing.py`.
The build fails when a Spanish string is no longer on the page (stale entry) or when the page has
Spanish text no entry covers (missing translation), so the three pages cannot drift apart silently.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / 'docs'

LANGUAGES = {
    'pt': {'html_lang': 'pt-BR', 'url': 'https://haxofi.com/pt/'},
    'en': {'html_lang': 'en', 'url': 'https://haxofi.com/en/'},
}

# Text that reads the same in every language (names, brands, commands).
SAME_EVERYWHERE = {
    'HaxOfi', 'HaxOfi · Haxball App', 'JEO', 'Varela', 'I0', 'HaxOfi | Haxball APP', 'OFICINA | FUTSAL HAXMAN RS JT',
    'Ranked', 'Clips', 'Stream', 'FPS', 'Ladder', 'GitHub', 'Discord HaxOfi', 'Discord Oficina', 'Apple Silicon',
    'Intel', 'xattr -cr /Applications/HaxOfi.app', 'ES', 'PT', 'EN',
}

# Each entry is a whole text node, attribute value, or element body (inline tags included), matched with any
# whitespace between words. Player-facing copy: no semicolons or dashes, button names exactly as each OS shows them.
STRINGS = [
    # head
    {'es': 'HaxOfi: Haxball gratis con ranked, Haxman, tienda, estadio con hinchada, clips de cada gol y más. Para Windows, Linux, Mac y Android.',
     'pt': 'HaxOfi: Haxball grátis com ranked, Haxman, loja, estádio com torcida, clipes de cada gol e mais. Para Windows, Linux, Mac e Android.',
     'en': 'HaxOfi: free Haxball with ranked, Haxman, a shop, a stadium full of fans, clips of every goal and more. For Windows, Linux, Mac and Android.'},
    {'es': 'Haxball gratis con ranked 1v1, 3v3, Real Soccer y Haxman, tienda de canchas y pelotas, estadio con recibimiento, tribuna y clips. Para Windows, Linux, Mac y Android.',
     'pt': 'Haxball grátis com ranked 1v1, 3v3, Real Soccer e Haxman, loja de campos e bolas, estádio com festa da torcida, arquibancada e clipes. Para Windows, Linux, Mac e Android.',
     'en': 'Free Haxball with 1v1, 3v3, Real Soccer and Haxman ranked, a shop of pitches and balls, a stadium with team entrances, stands and clips. For Windows, Linux, Mac and Android.'},
    {'es': 'Idioma', 'pt': 'Idioma', 'en': 'Language'},

    # hero
    {'es': 'Haxball con ranked,<br>estadio y hinchada',
     'pt': 'Haxball com ranked,<br>estádio e torcida',
     'en': 'Haxball with ranked,<br>stadium and fans'},
    {'es': 'Buscá partido con un botón, subí en el ladder y salí a la cancha con tu hinchada en la tribuna. Gratis para Windows, Linux, Mac y Android.',
     'pt': 'Procure partida com um botão, suba no ladder e entre em campo com sua torcida na arquibancada. Grátis para Windows, Linux, Mac e Android.',
     'en': 'Find a match with one button, climb the ladder and walk out with your fans in the stands. Free for Windows, Linux, Mac and Android.'},
    {'es': 'Descargar para Windows', 'pt': 'Baixar para Windows', 'en': 'Download for Windows'},
    {'es': 'Descargar para Linux', 'pt': 'Baixar para Linux', 'en': 'Download for Linux'},
    {'es': 'Descargar para Mac', 'pt': 'Baixar para Mac', 'en': 'Download for Mac'},
    {'es': 'Descargar para Android', 'pt': 'Baixar para Android', 'en': 'Download for Android'},
    {'es': 'Unite al Discord', 'pt': 'Entre no Discord', 'en': 'Join the Discord'},
    {'es': 'última versión', 'pt': 'última versão', 'en': 'latest version'},
    {'es': 'Todas las versiones', 'pt': 'Todas as versões', 'en': 'All versions'},

    # screenshots
    {'es': 'Recibimiento', 'pt': 'Festa da torcida', 'en': 'Team entrance'},
    {'es': 'Estadio lleno con humo, bengalas y la tribuna con los nombres de los hinchas',
     'pt': 'Estádio lotado com fumaça, sinalizadores e a arquibancada com o nome de cada torcedor',
     'en': 'Packed stadium with smoke, flares and the stands showing every fan by name'},
    {'es': 'captura pendiente', 'pt': 'captura pendente', 'en': 'screenshot pending'},
    {'es': 'Los equipos salen a la cancha con humo, bengalas y fuegos artificiales. Arriba, la tribuna con cada hincha y su nombre.',
     'pt': 'Os times entram em campo com fumaça, sinalizadores e fogos de artifício. Em cima, a arquibancada com cada torcedor e seu nome.',
     'en': 'Teams walk out to smoke, flares and fireworks. Up above, the stands show every fan by name.'},

    # discord cards
    {'es': '&nbsp;en línea ·&nbsp;', 'pt': '&nbsp;online ·&nbsp;', 'en': '&nbsp;online ·&nbsp;'},
    {'es': '&nbsp;miembros', 'pt': '&nbsp;membros', 'en': '&nbsp;members'},
    {'es': 'Unirse', 'pt': 'Entrar', 'en': 'Join'},

    # why HaxOfi
    {'es': 'Por qué HaxOfi', 'pt': 'Por que HaxOfi', 'en': 'Why HaxOfi'},
    {'es': 'Buscá partido', 'pt': 'Procure partida', 'en': 'Find a match'},
    {'es': '1v1, 3v3 y Real Soccer con elo por modo y un ladder con los mejores. En Haxman entran hasta treinta jugadores, cada uno defiende su arco y gana la última vida en pie.',
     'pt': '1v1, 3v3 e Real Soccer com elo por modo e um ladder com os melhores. No Haxman entram até trinta jogadores, cada um defende seu gol e vence quem sobrar com a última vida.',
     'en': '1v1, 3v3 and Real Soccer with elo per mode and a ladder of the best. Haxman takes up to thirty players, each one guards their own goal and the last life standing wins.'},
    {'es': 'Grupo', 'pt': 'Grupo', 'en': 'Party'},
    {'es': 'Jugá con amigos', 'pt': 'Jogue com amigos', 'en': 'Play with friends'},
    {'es': 'Armá grupo desde tu lista de amigos y caen todos del mismo lado. Cada uno marca su puesto, de arquero a delantero. Chat privado y quién está conectado.',
     'pt': 'Monte um grupo pela sua lista de amigos e todos caem no mesmo time. Cada um marca sua posição, de goleiro a atacante. Chat privado e quem está online.',
     'en': 'Form a party from your friends list and everyone lands on the same team. Each player picks a position, from keeper to striker. Private chat and who is online.'},
    {'es': 'Tienda', 'pt': 'Loja', 'en': 'Shop'},
    {'es': 'Nivel, fichas y tienda', 'pt': 'Nível, fichas e loja', 'en': 'Levels, tokens and shop'},
    {'es': 'Cada partido suma experiencia y fichas, más si ganás. Canjealas por canchas y pelotas con estela y sonido propio, y usalas en todos tus partidos.',
     'pt': 'Cada partida soma experiência e fichas, mais ainda se você ganhar. Troque por campos e bolas com rastro e som próprio e use em todas as suas partidas.',
     'en': 'Every match earns experience and tokens, more when you win. Trade them for pitches and balls with their own trail and sound, and use them in all your matches.'},
    {'es': 'Estadio', 'pt': 'Estádio', 'en': 'Stadium'},
    {'es': 'Tribunas con los colores de cada equipo, trapos, humo, bengalas y fuegos artificiales cuando los equipos salen a la cancha.',
     'pt': 'Arquibancadas com as cores de cada time, bandeirões, fumaça, sinalizadores e fogos de artifício quando os times entram em campo.',
     'en': 'Stands in each team\'s colours, banners, smoke, flares and fireworks as the teams walk out.'},
    {'es': 'Tribuna', 'pt': 'Arquibancada', 'en': 'Stands'},
    {'es': 'Alentá desde la tribuna', 'pt': 'Torça da arquibancada', 'en': 'Cheer from the stands'},
    {'es': 'Entrá a la tribuna de una sala con tu equipo, movete entre la gente y prendé bengalas, tres tiros y candelas.',
     'pt': 'Entre na arquibancada de uma sala com seu time, ande no meio da galera e acenda sinalizadores, rojões e velas romanas.',
     'en': 'Join a room\'s stands with your team, move through the crowd and light flares, firecrackers and roman candles.'},
    {'es': 'Clips de cada gol', 'pt': 'Clipes de cada gol', 'en': 'Clips of every goal'},
    {'es': 'Cada gol se repite en una esquina mientras el partido sigue. Con la C clipeás cualquier jugada y la bajás en MP4, lista para mandar por Discord.',
     'pt': 'Cada gol é repetido num canto enquanto a partida continua. Com a tecla C você clipa qualquer jogada e baixa em MP4, pronta para mandar no Discord.',
     'en': 'Every goal replays in a corner while the match goes on. Press C to clip any play and save it as an MP4, ready to post on Discord.'},

    # classic Haxball, improved
    {'es': 'Haxball de siempre, mejorado', 'pt': 'O Haxball de sempre, melhorado', 'en': 'Classic Haxball, improved'},
    {'es': 'Rotación', 'pt': 'Rotação', 'en': 'Rotation'},
    {'es': 'Siempre del mismo lado', 'pt': 'Sempre do mesmo lado', 'en': 'Always the same side'},
    {'es': 'Elegí izquierda o derecha y la cancha se da vuelta sola según tu equipo: siempre atacás para el mismo lado. También podés invertir la vista arriba/abajo si te resulta más cómodo.',
     'pt': 'Escolha esquerda ou direita e o campo vira sozinho conforme o seu time: você sempre ataca para o mesmo lado. Também dá para inverter a visão de cima para baixo se for mais confortável.',
     'en': 'Pick left or right and the pitch flips on its own to match your team: you always attack the same way. You can also flip the view top to bottom if that feels better.'},
    {'es': 'Salas', 'pt': 'Salas', 'en': 'Rooms'},
    {'es': 'Salas y host', 'pt': 'Salas e host', 'en': 'Rooms and hosting'},
    {'es': 'Lista de salas con favoritas, últimas visitadas y filtro por país. Si hosteás, cambiá nombre y cupo con la sala creada y activá plugins y modos como 8MAN o Real Soccer sin scripts.',
     'pt': 'Lista de salas com favoritas, últimas visitadas e filtro por país. Se você hosteia, mude o nome e o limite com a sala já criada e ative plugins e modos como 8MAN ou Real Soccer sem scripts.',
     'en': 'Room list with favourites, recently visited and a country filter. When you host, change the name and player limit after the room is up and turn on plugins and modes like 8MAN or Real Soccer without scripts.'},
    {'es': 'Modo streamer', 'pt': 'Modo streamer', 'en': 'Streamer mode'},
    {'es': 'Una ventana aparte con su propia extrapolación, el marcador, el minimapa, el chat y las teclas que apretás. Lista para capturar en OBS.',
     'pt': 'Uma janela separada com extrapolação própria, o placar, o minimapa, o chat e as teclas que você aperta. Pronta para capturar no OBS.',
     'en': 'A separate window with its own extrapolation, the scoreboard, the minimap, the chat and the keys you press. Ready to capture in OBS.'},
    {'es': 'Marcador', 'pt': 'Placar', 'en': 'Scoreboard'},
    {'es': 'Tres diseños con el escudo de la app, goleador y asistencia en cada gol y el alargue bajo el reloj. También podés armar el tuyo en HTML y CSS.',
     'pt': 'Três designs com o escudo do app, autor do gol e assistência em cada gol e a prorrogação embaixo do relógio. Você também pode montar o seu em HTML e CSS.',
     'en': 'Three designs with the app crest, scorer and assist on every goal and overtime under the clock. You can also build your own in HTML and CSS.'},
    {'es': 'Estilo', 'pt': 'Estilo', 'en': 'Style'},
    {'es': 'A tu gusto', 'pt': 'Do seu jeito', 'en': 'Your way'},
    {'es': 'Minimapa, pelota 3D que gira hacia donde va, colores de pelota y halo, camisetas propias, macros de chat y ocho temas para toda la app.',
     'pt': 'Minimapa, bola 3D que gira na direção em que vai, cores de bola e halo, camisas próprias, macros de chat e oito temas para todo o app.',
     'en': 'Minimap, a 3D ball that spins the way it travels, ball and halo colours, your own kits, chat macros and eight themes for the whole app.'},
    {'es': 'Rendimiento', 'pt': 'Desempenho', 'en': 'Performance'},
    {'es': 'Calidad gráfica en tres niveles: Media saca la pirotecnia y Baja también el estadio y los efectos de la pelota. Límite de FPS y escala de resolución para jugar fluido en cualquier PC.',
     'pt': 'Qualidade gráfica em três níveis: Média tira a pirotecnia e Baixa tira também o estádio e os efeitos da bola. Limite de FPS e escala de resolução para jogar liso em qualquer PC.',
     'en': 'Three graphics levels: Medium drops the pyrotechnics and Low also drops the stadium and ball effects. FPS cap and resolution scale for smooth play on any PC.'},

    # inside the app
    {'es': 'La app por dentro', 'pt': 'O app por dentro', 'en': 'Inside the app'},
    {'es': 'Jugar', 'pt': 'Jogar', 'en': 'Play'},
    {'es': 'Pantalla de ranked con un grupo de 3v3 armado', 'pt': 'Tela de ranked com um grupo de 3v3 montado', 'en': 'Ranked screen with a 3v3 party ready'},
    {'es': 'Elegí modo, armá grupo con amigos y marcá tu puesto. El partido arranca cuando todos aceptan.',
     'pt': 'Escolha o modo, monte um grupo com amigos e marque sua posição. A partida começa quando todos aceitam.',
     'en': 'Pick a mode, form a party with friends and mark your position. The match starts once everyone accepts.'},
    {'es': 'Gol', 'pt': 'Gol', 'en': 'Goal'},
    {'es': 'Gol en un estadio lleno con trapos de los dos equipos', 'pt': 'Gol num estádio lotado com bandeirões dos dois times', 'en': 'Goal in a packed stadium with banners from both teams'},
    {'es': 'Cada gol se celebra en el marcador y en las tribunas, con los trapos de cada equipo.',
     'pt': 'Cada gol é comemorado no placar e nas arquibancadas, com os bandeirões de cada time.',
     'en': 'Every goal is celebrated on the scoreboard and in the stands, with each team\'s banners.'},
    {'es': 'Resultado', 'pt': 'Resultado', 'en': 'Result'},
    {'es': 'Pantalla de victoria con elo, experiencia y fichas', 'pt': 'Tela de vitória com elo, experiência e fichas', 'en': 'Victory screen with elo, experience and tokens'},
    {'es': 'Al terminar, el elo ganado, la experiencia, las fichas y cada subida de nivel.',
     'pt': 'No fim, o elo ganho, a experiência, as fichas e cada subida de nível.',
     'en': 'At full time, the elo you won, experience, tokens and every level up.'},
    {'es': 'Pelotas', 'pt': 'Bolas', 'en': 'Balls'},
    {'es': 'Tienda de pelotas', 'pt': 'Loja de bolas', 'en': 'Ball shop'},
    {'es': 'Pelotas con estela y sonido propio. Cada una se ve como en la cancha antes de comprarla.',
     'pt': 'Bolas com rastro e som próprio. Cada uma aparece como em campo antes de comprar.',
     'en': 'Balls with their own trail and sound. Each one shows as it looks on the pitch before you buy it.'},
    {'es': 'Canchas', 'pt': 'Campos', 'en': 'Pitches'},
    {'es': 'Tienda de canchas', 'pt': 'Loja de campos', 'en': 'Pitch shop'},
    {'es': 'Canchas para 1v1 y 3v3, de las de la casa a las épicas. Algunas se desbloquean con nivel.',
     'pt': 'Campos para 1v1 e 3v3, dos da casa aos épicos. Alguns são desbloqueados por nível.',
     'en': 'Pitches for 1v1 and 3v3, from the house ones to the epic ones. Some unlock with level.'},
    {'es': 'Perfil', 'pt': 'Perfil', 'en': 'Profile'},
    {'es': 'Perfil con curva de elo e historial de partidos', 'pt': 'Perfil com curva de elo e histórico de partidas', 'en': 'Profile with elo curve and match history'},
    {'es': 'Curva de elo, rachas y el historial completo, con el detalle de cada partido.',
     'pt': 'Curva de elo, sequências e o histórico completo, com o detalhe de cada partida.',
     'en': 'Elo curve, streaks and your full history, with the details of every match.'},
    {'es': 'Ladder de 1v1 con el podio', 'pt': 'Ladder de 1v1 com o pódio', 'en': '1v1 ladder with the podium'},
    {'es': 'Los mejores de cada modo y tu puesto, siempre a la vista.',
     'pt': 'Os melhores de cada modo e a sua posição, sempre à vista.',
     'en': 'The best in every mode and your own rank, always in view.'},
    {'es': 'Lista de salas de Haxball con estadísticas de la sala elegida', 'pt': 'Lista de salas de Haxball com estatísticas da sala escolhida', 'en': 'Haxball room list with stats for the selected room'},
    {'es': 'Las salas de Haxball de siempre, con favoritas, filtro por país y las estadísticas de cada sala.',
     'pt': 'As salas de Haxball de sempre, com favoritas, filtro por país e as estatísticas de cada sala.',
     'en': 'The Haxball rooms you know, with favourites, a country filter and stats for every room.'},
    {'es': 'Ajustes', 'pt': 'Configurações', 'en': 'Settings'},
    {'es': 'Ajustes de juego', 'pt': 'Configurações de jogo', 'en': 'Game settings'},
    {'es': 'Jugá siempre del mismo lado y cambiá el fondo de la cancha, el halo y el grosor de discos y líneas.',
     'pt': 'Jogue sempre do mesmo lado e mude o fundo do campo, o halo e a espessura de discos e linhas.',
     'en': 'Always play the same side and change the pitch background, the halo and the thickness of discs and lines.'},

    # footer
    {'es': 'HaxOfi · hecho por', 'pt': 'HaxOfi · feito por', 'en': 'HaxOfi · made by'},
    {'es': 'Versiones', 'pt': 'Versões', 'en': 'Releases'},

    # install notices
    {'es': 'Ya se está descargando', 'pt': 'O download já começou', 'en': 'Your download has started'},
    {'es': 'Entendido', 'pt': 'Entendi', 'en': 'Got it'},
    {'es': 'La app no está firmada digitalmente, así que al abrirla Windows puede mostrar un aviso de SmartScreen: es solo que no compramos el certificado de firma.',
     'pt': 'O app não tem assinatura digital, então ao abrir o Windows pode mostrar um aviso do SmartScreen: é só porque não compramos o certificado de assinatura.',
     'en': 'The app is not digitally signed, so Windows may show a SmartScreen warning when you open it. We just have not bought a signing certificate.'},
    {'es': 'Si aparece el aviso, hacé clic en <b>Más información</b> y después en <b>Ejecutar de todas formas</b>.',
     'pt': 'Se o aviso aparecer, clique em <b>Mais informações</b> e depois em <b>Executar assim mesmo</b>.',
     'en': 'If the warning shows up, click <b>More info</b> and then <b>Run anyway</b>.'},
    {'es': 'SmartScreen no es un antivirus, solo avisa que la app no tiene firma: al continuar, tu antivirus sigue revisando la app como siempre.',
     'pt': 'O SmartScreen não é um antivírus, só avisa que o app não tem assinatura: ao continuar, seu antivírus segue verificando o app como sempre.',
     'en': 'SmartScreen is not an antivirus. It only warns that the app is unsigned, and your antivirus keeps checking the app as usual.'},
    {'es': '¿Qué Mac tenés?', 'pt': 'Qual Mac você tem?', 'en': 'Which Mac do you have?'},
    {'es': 'Abrí el menú Apple y entrá a <b>Acerca de esta Mac</b>. Si en <b>Chip</b> dice Apple M1, M2 o posterior, es Apple Silicon. Si dice <b>Procesador</b> Intel, es Intel.',
     'pt': 'Abra o menu Apple e entre em <b>Sobre Este Mac</b>. Se em <b>Chip</b> aparecer Apple M1, M2 ou posterior, é Apple Silicon. Se aparecer <b>Processador</b> Intel, é Intel.',
     'en': 'Open the Apple menu and choose <b>About This Mac</b>. If <b>Chip</b> says Apple M1, M2 or later, it is Apple Silicon. If it says <b>Processor</b> Intel, it is Intel.'},
    {'es': 'La app no está firmada por Apple, así que la primera vez macOS la bloquea al abrirla.',
     'pt': 'O app não é assinado pela Apple, então na primeira vez o macOS bloqueia ao abrir.',
     'en': 'The app is not signed by Apple, so macOS blocks it the first time you open it.'},
    {'es': 'Abrí el .dmg y arrastrá HaxOfi a <b>Aplicaciones</b>. Abrila una vez, cerrá el aviso y entrá a <b>Ajustes del Sistema</b>, <b>Privacidad y seguridad</b>. Abajo aparece HaxOfi: hacé clic en <b>Abrir igualmente</b>.',
     'pt': 'Abra o .dmg e arraste o HaxOfi para <b>Aplicativos</b>. Abra uma vez, feche o aviso e entre em <b>Ajustes do Sistema</b>, <b>Privacidade e Segurança</b>. Embaixo aparece o HaxOfi: clique em <b>Abrir Mesmo Assim</b>.',
     'en': 'Open the .dmg and drag HaxOfi to <b>Applications</b>. Open it once, close the warning and go to <b>System Settings</b>, <b>Privacy &amp; Security</b>. HaxOfi shows up at the bottom: click <b>Open Anyway</b>.'},
    {'es': 'Si macOS dice que la app está dañada, abrí la Terminal y pegá <b>xattr -cr /Applications/HaxOfi.app</b>',
     'pt': 'Se o macOS disser que o app está danificado, abra o Terminal e cole <b>xattr -cr /Applications/HaxOfi.app</b>',
     'en': 'If macOS says the app is damaged, open Terminal and paste <b>xattr -cr /Applications/HaxOfi.app</b>'},
    {'es': 'La app se instala desde el archivo .apk, no desde Play Store. Necesita Android 9 o posterior. Si estás en la compu, entrá a <b>haxofi.com</b> desde el celular.',
     'pt': 'O app é instalado pelo arquivo .apk, não pela Play Store. Precisa de Android 9 ou posterior. Se estiver no computador, abra <b>haxofi.com</b> no celular.',
     'en': 'The app installs from the .apk file, not from the Play Store. It needs Android 9 or later. On a computer? Open <b>haxofi.com</b> on your phone.'},
    {'es': 'Si el navegador avisa que el archivo puede ser dañino, tocá <b>Descargar de todas formas</b>.',
     'pt': 'Se o navegador avisar que o arquivo pode ser prejudicial, toque na opção de baixar mesmo assim.',
     'en': 'If the browser warns that the file might be harmful, tap <b>Download anyway</b>.'},
    {'es': 'Cuando termine la descarga, abrí el archivo. Si Android pide permiso para instalar apps desconocidas, tocá <b>Configuración</b>, activá <b>Permitir de esta fuente</b> y volvé atrás. Después tocá <b>Instalar</b>.',
     'pt': 'Quando o download terminar, abra o arquivo. Se o Android pedir permissão para instalar apps desconhecidos, toque em <b>Configurações</b>, ative <b>Permitir desta fonte</b> e volte. Depois toque em <b>Instalar</b>.',
     'en': 'When the download finishes, open the file. If Android asks for permission to install unknown apps, tap <b>Settings</b>, turn on <b>Allow from this source</b> and go back. Then tap <b>Install</b>.'},
    {'es': 'Si Play Protect avisa que no conoce la app, tocá <b>Más detalles</b> y después <b>Instalar de todas formas</b>. Las actualizaciones llegan desde la misma app.',
     'pt': 'Se o Play Protect avisar que não conhece o app, toque em <b>Mais detalhes</b> e depois na opção de instalar mesmo assim. As atualizações chegam pelo próprio app.',
     'en': 'If Play Protect says it does not recognise the app, tap <b>More details</b> and then <b>Install anyway</b>. Updates arrive through the app itself.'},
]

SCRIPT_OR_STYLE = re.compile(r'(<script\b.*?</script>|<style\b.*?</style>)', re.S | re.I)
UNSERVED_PREFIX = re.compile(r'^(?:[a-z]+:|//|/|#)', re.I)


def body_pattern(spanish):
    """Whole text node, attribute value or element body equal to `spanish`, any whitespace between words."""
    words = r'\s+'.join(re.escape(word) for word in spanish.split())
    return re.compile(r'(>\s*|=")' + words + r'(\s*<|")')


def translate_markup(markup, lang):
    """Translate every STRINGS entry outside <script> and <style>; returns (markup, Spanish strings matched)."""
    matched = set()
    entries = sorted(STRINGS, key=lambda entry: len(entry['es']), reverse=True)
    parts = SCRIPT_OR_STYLE.split(markup)
    for index in range(0, len(parts), 2):
        for entry in entries:
            translation = entry[lang]
            parts[index], count = body_pattern(entry['es']).subn(
                lambda match: match.group(1) + translation + match.group(2), parts[index])
            if count:
                matched.add(entry['es'])
    return ''.join(parts), matched


class VisibleText(HTMLParser):
    """Text nodes outside script/style plus the attribute values people read (alt, aria-label, meta copy)."""
    READ_ATTRIBUTES = {'alt', 'aria-label', 'title'}
    META_COPY = {'description', 'og:description', 'og:title'}

    def __init__(self):
        super().__init__()
        self.texts = set()
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip_depth += 1
        attributes = dict(attrs)
        for name in self.READ_ATTRIBUTES:
            self.add(attributes.get(name))
        if tag == 'meta' and (attributes.get('name') in self.META_COPY or attributes.get('property') in self.META_COPY):
            self.add(attributes.get('content'))

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            self.add(data)

    def add(self, text):
        text = ' '.join((text or '').replace('\xa0', ' ').split())
        if re.search(r'[^\W\d_]', text):
            self.texts.add(text)


def visible_text(markup):
    parser = VisibleText()
    parser.feed(markup)
    return parser.texts


def localize(markup, lang):
    """Language attribute, canonical/og URL, active switcher link, and relative links one folder up."""
    config = LANGUAGES[lang]
    markup = markup.replace('<html lang="es">', '<html lang="%s">' % config['html_lang'], 1)
    markup = markup.replace('<link rel="canonical" href="https://haxofi.com/">',
                            '<link rel="canonical" href="%s">' % config['url'], 1)
    markup = markup.replace('<meta property="og:url" content="https://haxofi.com/">',
                            '<meta property="og:url" content="%s">' % config['url'], 1)
    markup = markup.replace(' aria-current="page">ES</a>', '>ES</a>', 1)
    markup = markup.replace('hreflang="%s" lang="%s">' % ((config['html_lang'],) * 2),
                            'hreflang="%s" lang="%s" aria-current="page">' % ((config['html_lang'],) * 2), 1)
    markup = re.sub(r'\b(src|href)="([^"]*)"',
                    lambda match: match.group(0) if not match.group(2) or UNSERVED_PREFIX.match(match.group(2))
                    else '%s="../%s"' % (match.group(1), match.group(2)), markup)
    return '<!-- Generated by i18n/build_landing.py from docs/index.html. Edit that page, not this one. -->\n' + markup


def main():
    source = (DOCS / 'index.html').read_text(encoding='utf-8')
    spanish_text = visible_text(source)
    problems = []
    for lang in LANGUAGES:
        translated, matched = translate_markup(source, lang)
        for entry in STRINGS:
            if entry['es'] not in matched:
                problems.append('stale entry, not on the page: %r' % entry['es'])
        # Text nodes inside a translation's inline tags (<b>Chip</b>) count as translated too.
        translations = {' '.join(fragment.replace('&nbsp;', ' ').split())
                        for entry in STRINGS for fragment in re.split(r'<[^>]+>', entry[lang])}
        for text in sorted(visible_text(translated) & spanish_text):
            if text not in SAME_EVERYWHERE and text not in translations:
                problems.append('missing %s translation: %r' % (lang, text))
        out = DOCS / lang / 'index.html'
        out.parent.mkdir(exist_ok=True)
        out.write_text(localize(translated, lang), encoding='utf-8')
    if problems:
        sys.exit('\n'.join(sorted(set(problems))))
    print('wrote', ', '.join('docs/%s/index.html' % lang for lang in LANGUAGES))


if __name__ == '__main__':
    main()

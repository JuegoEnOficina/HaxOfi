// /<slug>/ pages: redirect to the matching asset of the latest release; fall back to the releases page.
(function () {
  var V = '[\\d.]+(-[\\w.]+)?';
  var ASSETS = {
    'base': 'AppHaxOfi-' + V + '-win\\.zip',
    'base-linux': 'HaxOfi-' + V + '-x86_64\\.AppImage',
    'base-mac-intel': 'HaxOfi-' + V + '-mac-x64\\.dmg',
    'base-mac-apple': 'HaxOfi-' + V + '-mac-arm64\\.dmg',
    'nt': 'AppNT-' + V + '-win\\.zip',
    'nt-linux': 'AppNT-' + V + '-x86_64\\.AppImage',
    'czapp': 'AppCZAPP-' + V + '-win\\.zip',
    'czapp-linux': 'AppCZAPP-' + V + '-x86_64\\.AppImage'
  };
  var FALLBACK = 'https://github.com/JuegoEnOficina/HaxOfi/releases/latest';
  var pattern = ASSETS[location.pathname.split('/')[1]];
  function go(url) { location.replace(url || FALLBACK); }
  if (!pattern) return go();
  var assetName = new RegExp('^' + pattern + '$', 'i');
  fetch('https://api.github.com/repos/JuegoEnOficina/HaxOfi/releases/latest')
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (rel) {
      var assets = (rel && rel.assets) || [];
      for (var i = 0; i < assets.length; i++)
        if (assetName.test(assets[i].name)) return go(assets[i].browser_download_url);
      go();
    })
    .catch(function () { go(); });
})();

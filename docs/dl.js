// Latest download per platform from the GitHub releases list. The /<slug>/ pages redirect to their asset (falling
// back to the releases page); the landing page loads this too and fills its buttons through window.haxofiDownloads.
(function () {
  var V = '[\\d.]+(-[\\w.]+)?';
  // Asset names per slug, most preferred first.
  var ASSETS = {
    'base': ['AppHaxOfi-' + V + '-win\\.zip'],
    'base-linux': ['HaxOfi-' + V + '-x86_64\\.AppImage'],
    'base-mac-intel': ['HaxOfi-' + V + '-mac-x64\\.dmg'],
    // Apple Silicon also runs the Intel build (Rosetta 2), so a newer Intel-only release beats an older native one.
    'base-mac-apple': ['HaxOfi-' + V + '-mac-arm64\\.dmg', 'HaxOfi-' + V + '-mac-x64\\.dmg'],
    'nt': ['AppNT-' + V + '-win\\.zip'],
    'nt-linux': ['AppNT-' + V + '-x86_64\\.AppImage'],
    'czapp': ['AppCZAPP-' + V + '-win\\.zip'],
    'czapp-linux': ['AppCZAPP-' + V + '-x86_64\\.AppImage']
  };
  var FALLBACK = 'https://github.com/JuegoEnOficina/HaxOfi/releases/latest';

  // Newest stable release that carries a build for the slug, as { url, tag }, or null. Prereleases are skipped
  // like /releases/latest does, and releases without the build are walked past: Mac builds stopped after 1.5.0.
  function findDownload(releases, slug) {
    var names = ASSETS[slug].map(function (pattern) { return new RegExp('^' + pattern + '$', 'i'); });
    for (var r = 0; r < releases.length; r++) {
      var release = releases[r];
      if (release.prerelease || release.draft) continue;
      for (var n = 0; n < names.length; n++)
        for (var a = 0; a < release.assets.length; a++)
          if (names[n].test(release.assets[a].name))
            return { url: release.assets[a].browser_download_url, tag: release.tag_name };
    }
    return null;
  }

  // Resolves to a slug -> download lookup; every lookup is null when the API is unreachable or rate limited.
  window.haxofiDownloads = fetch('https://api.github.com/repos/JuegoEnOficina/HaxOfi/releases')
    .then(function (r) { return r.ok ? r.json() : []; })
    .catch(function () { return []; })
    .then(function (releases) {
      return function (slug) { return findDownload(Array.isArray(releases) ? releases : [], slug); };
    });

  var slug = location.pathname.split('/')[1];
  if (!ASSETS[slug]) return;
  window.haxofiDownloads.then(function (download) {
    var found = download(slug);
    location.replace(found ? found.url : FALLBACK);
  });
})();

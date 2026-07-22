// The haxofi.com/<kind>/#<id> link pages. The id rides in the hash so one static file serves every link and GitHub
// Pages needs no routing. Each page says its kind, the shape its id must have and its words on <main>; this hands
// the id to the installed app as haxofi://<kind>/<id> (client src/lib/deepLink.js accepts exactly those shapes) and
// offers the download when no app answers.
(function () {
  var main = document.querySelector('main');
  var match = new RegExp('^#(' + main.dataset.id + ')$').exec(location.hash);
  var get = document.getElementById('get');
  if (!match) {
    document.getElementById('title').textContent = 'Enlace no válido';
    document.getElementById('lead').textContent = main.dataset.bad;
    get.hidden = false;
    return;
  }
  var link = 'haxofi://' + main.dataset.kind + '/' + match[1];
  var open = document.getElementById('open');
  open.href = link;
  open.hidden = false;
  // The browser asks before handing the link to the app; if the page is still in front two seconds later, the
  // app most likely is not installed (or the jump was blocked), so the download shows up next to the button.
  setTimeout(function () { if (document.visibilityState === 'visible') get.hidden = false; }, 2000);
  location.href = link;
})();

/* Anatomy of a Motorcycle — reader aids: bookmarks, continue reading, visited tracking.
   All state lives in localStorage on the reader's own device; nothing is sent anywhere.
   Hrefs are stored as absolute site paths (e.g. "/books/anatomy-of-a-motorcycle/chapter-9-12.html")
   so links work correctly no matter which page — library root or a book's own TOC — displays them.
   This requires the site to be served from its own origin (a real host, or a local server);
   opening files directly via file:// will not resolve the absolute paths. */
(function(){
  var LS_BOOKMARKS = "aoam_bookmarks";
  var LS_LAST_READ = "aoam_last_read";
  var LS_VISITED = "aoam_visited";

  function readJSON(key, fallback){
    try{
      var v = JSON.parse(localStorage.getItem(key));
      return v || fallback;
    }catch(e){ return fallback; }
  }
  function writeJSON(key, val){
    try{ localStorage.setItem(key, JSON.stringify(val)); }catch(e){}
  }
  function absPath(href){
    try{ return new URL(href, location.href).pathname; }catch(e){ return href; }
  }
  function currentHref(){
    return location.pathname;
  }
  function currentMeta(){
    var t = document.title.replace(/ \| [^|]+$/, "");
    return { slug: currentHref(), title: t, href: currentHref() };
  }

  function getBookmarks(){ return readJSON(LS_BOOKMARKS, []); }
  function setBookmarks(list){ writeJSON(LS_BOOKMARKS, list); }
  function isBookmarked(href){
    var list = getBookmarks();
    for(var i=0;i<list.length;i++){ if(list[i].href === href) return true; }
    return false;
  }
  function toggleBookmark(){
    var meta = currentMeta();
    var list = getBookmarks();
    var idx = -1;
    for(var i=0;i<list.length;i++){ if(list[i].href === meta.href){ idx = i; break; } }
    if(idx >= 0){ list.splice(idx, 1); } else { list.push(meta); }
    setBookmarks(list);
    updateBookmarkButton();
  }
  function updateBookmarkButton(){
    var btn = document.querySelector(".bookmark-toggle");
    var ribbon = document.querySelector(".page-ribbon");
    var active = isBookmarked(currentHref());
    if(btn) btn.classList.toggle("is-active", active);
    if(ribbon) ribbon.classList.toggle("show", active);
  }

  function recordVisit(){
    if(!document.querySelector(".tb-numeral")) return; // only actual chapter pages, not a book's TOC or the library
    var meta = currentMeta();
    writeJSON(LS_LAST_READ, meta);
    var visited = readJSON(LS_VISITED, []);
    if(visited.indexOf(meta.href) === -1){
      visited.push(meta.href);
      writeJSON(LS_VISITED, visited);
    }
  }

  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, function(c){
      return { "&":"&amp;", "<":"&lt;", ">":"&gt;", "\"":"&quot;", "'":"&#39;" }[c];
    });
  }

  var BOOKMARK_ICON = '<svg viewBox="0 0 24 24"><path d="M6 3.5h12a1 1 0 0 1 1 1V21l-7-4.2L5 21V4.5a1 1 0 0 1 1-1Z"/></svg>';

  function initContinueBanner(){
    var banner = document.getElementById("continueBanner");
    if(!banner) return;
    var last = readJSON(LS_LAST_READ, null);
    if(!last || !last.href || last.href === currentHref()) return;
    var titleEl = document.getElementById("continueTitle");
    var linkEl = document.getElementById("continueLink");
    if(titleEl) titleEl.textContent = last.title;
    if(linkEl) linkEl.setAttribute("href", last.href);
    banner.classList.add("show");
  }

  function initBookmarksPanel(){
    var panel = document.getElementById("bookmarksPanel");
    var list = document.getElementById("bookmarksList");
    if(!panel || !list) return;
    var bookmarks = getBookmarks();
    if(!bookmarks.length) return;
    list.innerHTML = bookmarks.map(function(b){
      return '<li><a href="' + escapeHtml(b.href) + '">' + BOOKMARK_ICON + escapeHtml(b.title) + "</a></li>";
    }).join("");
    panel.classList.add("show");
  }

  function markTocRows(){
    var rows = document.querySelectorAll("a.toc-row[href]");
    if(!rows.length) return;
    var bookmarkHrefs = getBookmarks().map(function(b){ return b.href; });
    var visited = readJSON(LS_VISITED, []);
    rows.forEach(function(row){
      var abs = absPath(row.getAttribute("href"));
      if(bookmarkHrefs.indexOf(abs) !== -1){
        row.classList.add("is-bookmarked");
        var mark = document.createElement("span");
        mark.className = "row-bm";
        mark.innerHTML = BOOKMARK_ICON;
        var titleEl = row.querySelector(".title");
        if(titleEl) titleEl.appendChild(mark);
      }
      if(visited.indexOf(abs) !== -1){
        row.classList.add("is-visited");
      }
    });
  }

  function initLibraryContinue(){
    var card = document.querySelector(".book-card[data-book]");
    if(!card) return;
    var last = readJSON(LS_LAST_READ, null);
    if(!last || !last.href) return;
    var badge = document.createElement("span");
    badge.className = "cb-continue";
    badge.textContent = "Continue: " + last.title;
    card.appendChild(badge);
    card.setAttribute("href", last.href);
  }

  window.aoamToggleBookmark = toggleBookmark;

  document.addEventListener("DOMContentLoaded", function(){
    updateBookmarkButton();
    recordVisit();
    initContinueBanner();
    initBookmarksPanel();
    markTocRows();
    initLibraryContinue();
  });
})();

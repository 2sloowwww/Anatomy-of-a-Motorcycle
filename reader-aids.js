/* Knowbase — reader aids: bookmarks, continue reading, visited tracking.
   All state lives in localStorage on the reader's own device; nothing is sent anywhere.
   Hrefs are stored as absolute site paths (e.g. "/books/anatomy-of-a-motorcycle/chapter-9-12.html")
   so links work correctly no matter which page — library root or a book's own TOC — displays them.
   This requires the site to be served from its own origin (a real host, or a local server);
   opening files directly via file:// will not resolve the absolute paths. */
(function(){
  var LS_BOOKMARKS = "aoam_bookmarks";
  var LS_LAST_READ = "aoam_last_read";
  var LS_VISITED = "aoam_visited";

  var LOCKED_PREFIXES = ["/books/davinci-resolve-editing/"];
  function isLocked(href){ if(!href) return false; for(var i=0;i<LOCKED_PREFIXES.length;i++){ if(href.indexOf(LOCKED_PREFIXES[i]) === 0) return true; } return false; }
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
    // Built from the page itself (not <title>, which is SEO-shortened): "4.5 — Countersteering"
    var num = document.querySelector(".tb-numeral"), h1 = document.querySelector("h1");
    var t = (num && h1) ? num.textContent.trim() + " — " + h1.textContent.trim() : document.title.replace(/ [|—] [^|—]+$/, "");
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
    if(!last || !last.href || isLocked(last.href) || last.href === currentHref()) return;
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
    var bookmarks = getBookmarks().filter(function(b){ return !isLocked(b.href); });
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
    if(!last || !last.href || isLocked(last.href)) return;
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


/* ==========================================================================
   Knowbase reading experience — progress bar, sticky chapter bar, outline,
   text controls, keyboard navigation, diagram zoom, share row, TOC progress.
   Everything is progressive enhancement: pages stay fully readable without it.
   Preferences live in localStorage on the reader's own device.
   ========================================================================== */
(function(){
  var PREFS_KEY = "knowbase_read_prefs";
  var SIZES = [0.92, 1, 1.1, 1.22, 1.36];
  function jget(k, f){ try{ var v = JSON.parse(localStorage.getItem(k)); return v == null ? f : v; }catch(e){ return f; } }
  function jset(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function el(tag, cls, html){ var n = document.createElement(tag); if(cls) n.className = cls; if(html != null) n.innerHTML = html; return n; }
  function slug(t){ return t.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60); }
  function esc(s){ return String(s).replace(/[&<>"']/g, function(c){ return { "&":"&amp;", "<":"&lt;", ">":"&gt;", "\"":"&quot;", "'":"&#39;" }[c]; }); }

  /* ---------- preferences (applied immediately to avoid a flash) ---------- */
  var prefs = jget(PREFS_KEY, { size: 1, wide: false });
  function applyPrefs(){
    var r = document.documentElement;
    r.style.setProperty("--read-scale", SIZES[prefs.size] || 1);
    r.classList.toggle("read-wide", !!prefs.wide);
  }
  applyPrefs();

  var lb = null;
  function closeLightbox(){ if(lb){ lb.remove(); lb = null; document.body.classList.remove("lb-open"); } }

  function initChapter(){
    var article = document.querySelector("article");
    if(!article || !document.querySelector(".tb-numeral")) return;
    document.body.classList.add("is-chapter");

    var numeral = document.querySelector(".tb-numeral");
    var h1 = document.querySelector(".tb-titlewrap h1");
    var series = document.querySelector(".tb-top .series");
    var canonicalEl = document.querySelector('link[rel="canonical"]');
    var canonical = canonicalEl ? canonicalEl.href : location.href;
    var title = h1 ? h1.textContent.trim() : document.title;
    var code = numeral ? numeral.textContent.trim() : "";

    /* ----- sticky reading bar with progress ----- */
    var bar = el("div", "read-bar");
    bar.setAttribute("role", "navigation");
    bar.setAttribute("aria-label", "Reading progress");
    bar.innerHTML =
      '<a class="rb-back" href="' + esc(series ? series.getAttribute("href") : "index.html") + '">&larr; <span>' + esc(series ? series.textContent.trim() : "Contents") + '</span></a>' +
      '<span class="rb-title"><b>' + esc(code) + '</b> ' + esc(title) + '</span>' +
      '<span class="rb-left"></span>' +
      '<span class="rb-progress"><i></i></span>';
    document.body.appendChild(bar);
    var fill = bar.querySelector(".rb-progress i");
    var left = bar.querySelector(".rb-left");
    var words = (article.textContent.match(/\S+/g) || []).length;
    var railUpdate = null;

    function onScroll(){
      var y = window.scrollY || document.documentElement.scrollTop;
      var top = article.getBoundingClientRect().top + y;
      var span = Math.max(1, article.offsetHeight - window.innerHeight * 0.5);
      var pct = Math.max(0, Math.min(1, (y + window.innerHeight * 0.3 - top) / span));
      fill.style.transform = "scaleX(" + pct + ")";
      bar.classList.toggle("show", y > 220);
      var mins = Math.ceil((words * (1 - pct)) / 230);
      left.textContent = pct >= 0.98 ? "Finished" : (mins <= 1 ? "<1 min left" : mins + " min left");
      if(railUpdate) railUpdate();
    }
    var ticking = false;
    window.addEventListener("scroll", function(){
      if(!ticking){ ticking = true; requestAnimationFrame(function(){ onScroll(); ticking = false; }); }
    }, { passive: true });
    window.addEventListener("resize", onScroll);
    onScroll();

    /* ----- section anchors + outline rail ----- */
    var heads = Array.prototype.slice.call(article.querySelectorAll("h2.section"));
    var used = {};
    heads.forEach(function(h){
      var id = h.id || slug(h.textContent) || "section";
      var base = id, n = 2;
      while(used[id]){ id = base + "-" + n++; }
      used[id] = 1; h.id = id;
    });
    if(heads.length > 2){
      var rail = el("nav", "outline-rail");
      rail.setAttribute("aria-label", "On this page");
      rail.innerHTML = '<span class="or-label">On this page</span><ol>' + heads.map(function(h){
        return '<li><a href="#' + h.id + '">' + esc(h.textContent.trim()) + '</a></li>';
      }).join("") + '</ol>';
      document.body.appendChild(rail);
      var links = rail.querySelectorAll("a");
      railUpdate = function(){
        var cur = null;
        for(var i = 0; i < heads.length; i++){ if(heads[i].getBoundingClientRect().top < 150) cur = heads[i].id; else break; }
        links.forEach(function(a){ a.classList.toggle("active", !!cur && a.getAttribute("href") === "#" + cur); });
      };
      railUpdate();
    }

    /* ----- text controls ----- */
    var btn = el("button", "rd-fab", "Aa");
    btn.type = "button";
    btn.setAttribute("aria-label", "Reading settings");
    btn.setAttribute("aria-expanded", "false");
    var pop = el("div", "rd-pop");
    pop.setAttribute("role", "dialog");
    pop.setAttribute("aria-label", "Reading settings");
    pop.innerHTML =
      '<div class="rd-row"><span>Text size</span><div class="rd-seg"><button type="button" data-act="smaller" aria-label="Smaller text">A&minus;</button><button type="button" data-act="bigger" aria-label="Larger text">A+</button></div></div>' +
      '<div class="rd-row"><span>Line width</span><div class="rd-seg"><button type="button" data-act="narrow">Comfort</button><button type="button" data-act="wide">Wide</button></div></div>' +
      '<div class="rd-row rd-hint">Tip: press <kbd>&larr;</kbd> <kbd>&rarr;</kbd> to move between chapters.</div>';
    document.body.appendChild(pop);
    document.body.appendChild(btn);
    function syncPop(){
      pop.querySelector('[data-act="narrow"]').classList.toggle("on", !prefs.wide);
      pop.querySelector('[data-act="wide"]').classList.toggle("on", !!prefs.wide);
      pop.querySelector('[data-act="smaller"]').disabled = prefs.size <= 0;
      pop.querySelector('[data-act="bigger"]').disabled = prefs.size >= SIZES.length - 1;
    }
    syncPop();
    btn.addEventListener("click", function(e){
      e.stopPropagation();
      var o = pop.classList.toggle("open");
      btn.setAttribute("aria-expanded", o ? "true" : "false");
    });
    document.addEventListener("click", function(e){
      if(!pop.contains(e.target) && e.target !== btn){ pop.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); }
    });
    pop.addEventListener("click", function(e){
      var a = e.target.getAttribute && e.target.getAttribute("data-act");
      if(!a) return;
      if(a === "smaller") prefs.size = Math.max(0, prefs.size - 1);
      if(a === "bigger") prefs.size = Math.min(SIZES.length - 1, prefs.size + 1);
      if(a === "narrow") prefs.wide = false;
      if(a === "wide") prefs.wide = true;
      jset(PREFS_KEY, prefs); applyPrefs(); syncPop(); onScroll();
    });

    /* ----- keyboard navigation between chapters ----- */
    document.addEventListener("keydown", function(e){
      if(e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) return;
      var t = e.target;
      if(t && (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable)) return;
      if(e.key === "Escape"){ pop.classList.remove("open"); closeLightbox(); return; }
      var dest = null;
      if(e.key === "ArrowLeft") dest = document.querySelector(".chapter-nav a.prev");
      if(e.key === "ArrowRight") dest = document.querySelector(".chapter-nav a.next");
      if(dest) location.href = dest.getAttribute("href");
    });

    /* ----- diagram zoom ----- */
    article.querySelectorAll(".diagram-img").forEach(function(img){
      img.setAttribute("tabindex", "0");
      img.setAttribute("role", "button");
      img.setAttribute("title", "Click to enlarge");
      function open(){
        lb = el("div", "lightbox");
        lb.innerHTML = '<button type="button" class="lb-close" aria-label="Close">&times;</button><img src="' + esc(img.currentSrc || img.src) + '" alt="' + esc(img.alt) + '">';
        lb.addEventListener("click", closeLightbox);
        document.body.appendChild(lb);
        document.body.classList.add("lb-open");
      }
      img.addEventListener("click", open);
      img.addEventListener("keydown", function(e){ if(e.key === "Enter" || e.key === " "){ e.preventDefault(); open(); } });
    });

    /* ----- share row before the chapter navigation ----- */
    var nav = document.querySelector(".chapter-nav");
    if(nav){
      var text = code + " — " + title + " · " + (series ? series.textContent.trim() : "Knowbase");
      var u = encodeURIComponent(canonical), t = encodeURIComponent(text);
      var share = el("section", "share-row");
      share.innerHTML =
        '<div class="sr-copy"><b>Know someone who would get value from this?</b><span>Every chapter is free to read — send it on.</span></div>' +
        '<div class="sr-actions">' +
          '<button type="button" class="sr-btn" data-share="copy">Copy link</button>' +
          '<a class="sr-btn" target="_blank" rel="noopener" href="https://wa.me/?text=' + t + '%20' + u + '">WhatsApp</a>' +
          '<a class="sr-btn" target="_blank" rel="noopener" href="https://twitter.com/intent/tweet?text=' + t + '&amp;url=' + u + '">X</a>' +
          '<a class="sr-btn" target="_blank" rel="noopener" href="https://www.linkedin.com/sharing/share-offsite/?url=' + u + '">LinkedIn</a>' +
          '<a class="sr-btn" href="mailto:?subject=' + t + '&amp;body=' + u + '">Email</a>' +
        '</div>';
      nav.parentNode.insertBefore(share, nav);
      var copyBtn = share.querySelector('[data-share="copy"]');
      copyBtn.addEventListener("click", function(){
        function ok(){ copyBtn.textContent = "Copied ✓"; setTimeout(function(){ copyBtn.textContent = "Copy link"; }, 1800); }
        if(navigator.share && /Mobi|Android/i.test(navigator.userAgent)){ navigator.share({ title: text, url: canonical }).catch(function(){}); return; }
        if(navigator.clipboard){ navigator.clipboard.writeText(canonical).then(ok, function(){ window.prompt("Copy this link:", canonical); }); }
        else { window.prompt("Copy this link:", canonical); }
      });
    }
  }

  /* ---------- book contents page: per-part and overall progress ---------- */
  function initToc(){
    var parts = document.querySelectorAll(".toc-part");
    if(!parts.length || document.querySelector(".tb-numeral")) return;
    var visited = jget("aoam_visited", []);
    var total = 0, read = 0;
    parts.forEach(function(p){
      var rows = p.querySelectorAll("a.toc-row.is-live");
      var n = 0;
      rows.forEach(function(r){
        var path;
        try{ path = new URL(r.getAttribute("href"), location.href).pathname; }catch(e){ return; }
        if(visited.indexOf(path) !== -1) n++;
      });
      total += rows.length; read += n;
      var count = p.querySelector(".count");
      if(count && rows.length && n){
        count.parentNode.insertBefore(el("span", "part-read", n + "/" + rows.length + " read"), count);
      }
    });
    var anchor = document.getElementById("continueBanner");
    if(read && anchor){
      var pct = Math.round(read / total * 100);
      var strip = el("div", "toc-progress");
      strip.innerHTML = '<div><b>Your progress</b> · ' + read + ' of ' + total + ' chapters read (' + pct + '%)</div><span class="tp-bar"><i style="width:' + pct + '%"></i></span>';
      anchor.parentNode.insertBefore(strip, anchor);
    }
  }

  document.addEventListener("DOMContentLoaded", function(){ initChapter(); initToc(); });
})();


/* ==========================================================================
   Knowbase engagement layer — living diagrams, "up next" pull, completion
   moments, reading streak, staged reveals. Progressive enhancement only.
   ========================================================================== */
(function(){
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function jget(k, f){ try{ var v = JSON.parse(localStorage.getItem(k)); return v == null ? f : v; }catch(e){ return f; } }
  function jset(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function el(tag, cls, html){ var n = document.createElement(tag); if(cls) n.className = cls; if(html != null) n.innerHTML = html; return n; }
  function esc(s){ return String(s).replace(/[&<>"']/g, function(c){ return { "&":"&amp;", "<":"&lt;", ">":"&gt;", "\"":"&quot;", "'":"&#39;" }[c]; }); }

  /* ---------- living diagrams ---------- */
  var KB = window.KBDiagram = {
    prepare: function(svg){
      svg.querySelectorAll(".draw").forEach(function(n){
        var L = 0; try{ L = n.getTotalLength(); }catch(e){}
        if(!L || !isFinite(L)) L = 1200;
        n.style.setProperty("--len", Math.ceil(L) + 2);
        n.style.setProperty("--i", n.getAttribute("data-i") || 0);
      });
      svg.querySelectorAll(".pop, .fade").forEach(function(n){ n.style.setProperty("--i", n.getAttribute("data-i") || 0); });
    },
    play: function(svg){ svg.classList.remove("play"); void svg.getBoundingClientRect(); svg.classList.add("play"); },
    mount: function(container, text, label){
      container.innerHTML = text;
      var svg = container.querySelector("svg"); if(!svg) return null;
      svg.setAttribute("role", "img"); if(label) svg.setAttribute("aria-label", label);
      if(svg.classList.contains("dg")){ KB.prepare(svg); requestAnimationFrame(function(){ requestAnimationFrame(function(){ KB.play(svg); }); }); }
      return svg;
    }
  };

  function closeBox(box){ if(box && box.parentNode){ box.parentNode.removeChild(box); document.body.classList.remove("lb-open"); } }
  function inlineDiagrams(){
    var imgs = document.querySelectorAll("article img.diagram-img");
    imgs.forEach(function(img){
      var src = img.getAttribute("src") || ""; if(!/\.svg(\?|$)/.test(src)) return;
      fetch(src).then(function(r){ return r.ok ? r.text() : Promise.reject(); }).then(function(t){
        if(t.indexOf("class=\"dg") === -1) return; // legacy drawings stay as images
        var wrap = el("div", "diagram-svg");
        wrap.setAttribute("tabindex", "0"); wrap.setAttribute("title", "Click to enlarge");
        img.parentNode.replaceChild(wrap, img);
        var svg = KB.mount(wrap, t, img.alt); if(!svg) return;
        function open(){
          var box = el("div", "lightbox"); box.innerHTML = '<button type="button" class="lb-close" aria-label="Close">&times;</button><div class="lb-svg"></div>';
          box.querySelector(".lb-svg").innerHTML = wrap.innerHTML;
          var s2 = box.querySelector("svg"); if(s2){ s2.classList.add("play"); KB.prepare(s2); s2.classList.add("play"); }
          box.addEventListener("click", function(){ closeBox(box); });
          document.addEventListener("keydown", function esc1(e){ if(e.key === "Escape"){ closeBox(box); document.removeEventListener("keydown", esc1); } });
          document.body.appendChild(box); document.body.classList.add("lb-open");
        }
        wrap.addEventListener("click", open);
        wrap.addEventListener("keydown", function(e){ if(e.key === "Enter"){ open(); } });
        // replay each time it scrolls back into view for the first time only; start paused until visible
        svg.classList.remove("play");
        if("IntersectionObserver" in window){
          var io = new IntersectionObserver(function(es){ if(es[0].isIntersecting){ KB.play(svg); io.disconnect(); } }, { threshold: 0.35 });
          io.observe(wrap);
        } else { KB.play(svg); }
        // re-play on click of the figure tag
        var tag = wrap.parentNode.querySelector(".dtag"); if(tag){ tag.style.cursor = "pointer"; tag.title = "Replay"; tag.addEventListener("click", function(e){ e.stopPropagation(); KB.play(svg); }); }
      }).catch(function(){});
    });
  }

  /* ---------- streak + completion + up-next ---------- */
  function dayKey(d){ return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate(); }
  function touchStreak(){
    var s = jget("knowbase_streak", { last: null, days: 0 }), t = dayKey(new Date());
    if(s.last === t) return s;
    s.days = (s.last === dayKey(new Date(Date.now() - 864e5))) ? s.days + 1 : 1; s.last = t; jset("knowbase_streak", s); return s;
  }
  function toast(html){
    var old = document.querySelector(".kb-toast"); if(old) old.remove();
    var t = el("div", "kb-toast", html); document.body.appendChild(t);
    requestAnimationFrame(function(){ t.classList.add("in"); });
    setTimeout(function(){ t.classList.remove("in"); setTimeout(function(){ t.remove(); }, 500); }, 6500);
  }
  function bookPrefix(){ var m = location.pathname.match(/^\/books\/[^/]+\//); return m ? m[0] : ""; }

  function initEngage(){
    var article = document.querySelector("article");
    if(!article || !document.querySelector(".tb-numeral")) return;
    var streak = touchStreak();
    var code = (document.querySelector(".tb-numeral") || {}).textContent || "";
    inlineDiagrams();

    /* staged reveals for the "designed" blocks, never the body text */
    if(!reduced && "IntersectionObserver" in window){
      var rv = article.querySelectorAll(".pull, .plate, .refs, h2.section");
      rv.forEach(function(n){ n.classList.add("rv"); });
      article.querySelectorAll(".plate li").forEach(function(li, i){ li.classList.add("rv"); li.style.transitionDelay = (i % 6) * 0.09 + "s"; });
      var io2 = new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add("rv-in"); io2.unobserve(e.target); } }); }, { threshold: 0.15, rootMargin: "0px 0px -6% 0px" });
      article.querySelectorAll(".rv").forEach(function(n){ io2.observe(n); });
    }

    /* "Up next" card: the strongest reason to keep reading */
    var nav = document.querySelector(".chapter-nav"), nextA = document.querySelector(".chapter-nav a.next");
    var card = el("section", "upnext");
    if(nextA){
      var href = nextA.getAttribute("href"), ttl = (nextA.querySelector(".ttl") || {}).textContent || "Next chapter";
      card = el("a", "upnext"); card.href = href;
      card.innerHTML = '<span class="un-k">Up next</span><span class="un-title">' + esc(ttl) + '</span><span class="un-d">Loading a preview…</span><span class="un-go">Continue reading <i>&rarr;</i></span><span class="un-bar"><i></i></span>';
      fetch(href).then(function(r){ return r.text(); }).then(function(html){
        var doc = new DOMParser().parseFromString(html, "text/html");
        var lede = doc.querySelector(".lede"), fields = doc.querySelectorAll(".tb-field .fv"), mins = "";
        fields.forEach(function(f){ if(/min/i.test(f.textContent)) mins = f.textContent.replace("~", "").trim(); });
        var txt = lede ? lede.textContent.trim().replace(/\s+/g, " ") : "";
        if(txt.length > 170){ txt = txt.slice(0, 170).replace(/\s+\S*$/, "") + "…"; }
        card.querySelector(".un-d").textContent = txt || "Keep going — the next chapter builds directly on this one.";
        if(mins){ card.querySelector(".un-k").textContent = "Up next · about " + mins.toLowerCase(); }
      }).catch(function(){ card.querySelector(".un-d").textContent = "Keep going — the next chapter builds directly on this one."; });
    } else {
      card.classList.add("end");
      card.innerHTML = '<span class="un-k">The end of this book</span><span class="un-title">Thank you for reading it all.</span><span class="un-d">If it helped, tell me which chapter landed best — it genuinely shapes what I write next.</span><a class="un-go" href="https://instagram.com/2sloowwww" target="_blank" rel="noopener">Say hi on Instagram <i>&rarr;</i></a>';
    }
    var share = document.querySelector(".share-row");
    var anchor = share || nav; if(anchor) anchor.parentNode.insertBefore(card, anchor);

    /* completion moment, once per chapter per day */
    var key = "kb_done_" + location.pathname, fired = false;
    function checkDone(){
      if(fired) return;
      var doc = document.documentElement, y = window.scrollY, max = doc.scrollHeight - innerHeight;
      var cardTop = card.getBoundingClientRect().top;
      if(max > 0 && (y / max > 0.97 || cardTop < innerHeight * 0.8)){
        fired = true;
        var done = jget(key, null), today = dayKey(new Date());
        if(done === today) return;
        jset(key, today);
        var pre = bookPrefix(), visited = jget("aoam_visited", []).filter(function(h){ return pre && h.indexOf(pre) === 0; });
        toast('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle class="tc" cx="12" cy="12" r="10"/><path class="tk" d="M7 12.5l3.2 3.2L17 9"/></svg><div><b>Chapter ' + esc(code) + ' complete</b><span>' + visited.length + ' chapter' + (visited.length === 1 ? "" : "s") + ' read in this book' + (streak.days > 1 ? ' &middot; ' + streak.days + '-day reading streak' : '') + '</span></div>');
      }
    }
    window.addEventListener("scroll", checkDone, { passive: true });
    setTimeout(checkDone, 600);
  }
  document.addEventListener("DOMContentLoaded", initEngage);
})();


/* ==========================================================================
   Knowbase audience layer — email signup (Netlify Forms) + optional analytics.
   Any <form class="kb-signup"> on the site is wired up here; chapters get one
   automatically. The static form in index.html registers "knowbase-signup"
   with Netlify at deploy time.
   ========================================================================== */
(function(){
  /* Privacy-friendly analytics: set to your Plausible site domain (e.g. "knowbase.xyz") to switch on. */
  var PLAUSIBLE_DOMAIN = "";
  if(PLAUSIBLE_DOMAIN){
    var ps = document.createElement("script");
    ps.defer = true; ps.setAttribute("data-domain", PLAUSIBLE_DOMAIN); ps.src = "https://plausible.io/js/script.js";
    document.head.appendChild(ps);
  }

  function isSubscribed(){ try{ return localStorage.getItem("kb_subscribed") === "1"; }catch(e){ return false; } }

  function bind(form){
    if(form.__kb) return; form.__kb = true;
    var msg = form.querySelector(".kb-su-msg"), btn = form.querySelector("button[type=submit]");
    form.addEventListener("submit", function(e){
      e.preventDefault();
      var email = (form.elements.email.value || "").trim();
      if(!/^\S+@\S+\.\S+$/.test(email)){ msg.textContent = "That email doesn’t look right — mind checking it?"; msg.className = "kb-su-msg err"; return; }
      btn.disabled = true; msg.textContent = "Adding you…"; msg.className = "kb-su-msg";
      fetch("/", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams(new FormData(form)).toString() })
        .then(function(r){ if(!r.ok) throw new Error("bad"); })
        .then(function(){
          try{ localStorage.setItem("kb_subscribed", "1"); }catch(e){}
          form.classList.add("done");
          msg.textContent = "You’re on the list ✓ I’ll email you when the next manual opens.";
          msg.className = "kb-su-msg ok";
        })
        .catch(function(){ btn.disabled = false; msg.textContent = "Couldn’t save that just now — please try again in a moment."; msg.className = "kb-su-msg err"; });
    });
  }

  function chapterBlock(){
    var share = document.querySelector(".share-row");
    if(!share || !document.querySelector(".tb-numeral") || isSubscribed()) return;
    var sec = document.createElement("section");
    sec.className = "kb-su-card";
    sec.innerHTML =
      '<div class="kb-su-copy"><b>Get the next manual first.</b><span>One email when a new Knowbase manual opens &mdash; and now and then a diagram worth keeping. No spam, unsubscribe any time.</span></div>' +
      '<form class="kb-signup" name="knowbase-signup" method="POST" data-netlify="true" netlify-honeypot="bot-field">' +
        '<input type="hidden" name="form-name" value="knowbase-signup">' +
        '<input type="hidden" name="source" value="' + location.pathname.replace(/"/g, "") + '">' +
        '<p class="kb-hp"><label>Skip this <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>' +
        '<div class="kb-su-row"><input type="email" name="email" placeholder="you@email.com" required autocomplete="email" aria-label="Email address"><button type="submit">Notify me</button></div>' +
        '<div class="kb-su-msg" role="status" aria-live="polite"></div>' +
      '</form>';
    share.parentNode.insertBefore(sec, share);
    bind(sec.querySelector("form"));
  }

  document.addEventListener("DOMContentLoaded", function(){
    chapterBlock();
    document.querySelectorAll("form.kb-signup").forEach(function(f){
      if(isSubscribed()){ f.classList.add("done"); var m = f.querySelector(".kb-su-msg"); if(m){ m.textContent = "You’re already on the list ✓"; m.className = "kb-su-msg ok"; } }
      bind(f);
    });
  });
})();

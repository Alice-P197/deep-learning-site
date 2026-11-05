// 深度学习学习站 · 交互脚本
(function () {
  "use strict";

  var KEY = "dlsite-progress-v1";

  function readProgress() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "{}") || {};
    } catch (e) {
      return {};
    }
  }

  function writeProgress(p) {
    try {
      localStorage.setItem(KEY, JSON.stringify(p));
    } catch (e) {
      /* 隐私模式下静默失败 */
    }
  }

  var progress = readProgress();

  /* 1. 侧边栏进度与勾选标记 */
  var pages = document.querySelectorAll(".nav-item[data-page]");
  var chapters = document.querySelectorAll(".nav-item[data-chapter='1']");
  var total = 16;

  function paintProgress() {
    var done = 0;
    chapters.forEach(function (item) {
      var slug = item.getAttribute("data-page");
      if (progress[slug]) {
        item.classList.add("done");
        done += 1;
      } else {
        item.classList.remove("done");
      }
    });
    var bar = document.getElementById("progress-bar");
    var count = document.getElementById("progress-count");
    var homeBar = document.getElementById("home-bar");
    var homeCount = document.getElementById("home-count");
    var pct = Math.round((done / total) * 100);
    if (bar) bar.style.width = pct + "%";
    if (count) count.textContent = done + " / " + total;
    if (homeBar) homeBar.style.width = pct + "%";
    if (homeCount) {
      homeCount.textContent =
        done === 0
          ? "尚未开始，建议从第 1 章读起"
          : "已完成 " + done + " / " + total + " 章（" + pct + "%）";
    }
  }

  /* 2. 标记本章已学完 */
  var slug = document.body.getAttribute("data-slug");
  var markBtn = document.getElementById("mark-done");
  if (markBtn && slug) {
    if (progress[slug]) {
      markBtn.classList.add("on");
      markBtn.textContent = "已标记完成 ✓";
    }
    markBtn.addEventListener("click", function () {
      if (progress[slug]) {
        delete progress[slug];
        markBtn.classList.remove("on");
        markBtn.textContent = "标记本章已学完";
      } else {
        progress[slug] = true;
        markBtn.classList.add("on");
        markBtn.textContent = "已标记完成 ✓";
      }
      writeProgress(progress);
      paintProgress();
    });
  }
  paintProgress();

  /* 3. 代码复制 */
  document.querySelectorAll(".code .copy").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var box = btn.closest(".code");
      var pre = box ? box.querySelector("pre") : null;
      if (!pre) return;
      var text = pre.innerText;
      var done = function () {
        btn.textContent = "已复制";
        btn.classList.add("ok");
        setTimeout(function () {
          btn.textContent = "复制";
          btn.classList.remove("ok");
        }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {
          fallback(text, done);
        });
      } else {
        fallback(text, done);
      }
    });
  });

  function fallback(text, done) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand("copy");
      done();
    } catch (e) {
      /* 忽略 */
    }
    document.body.removeChild(ta);
  }

  /* 4. 侧边栏筛选 */
  var search = document.getElementById("nav-search");
  if (search) {
    var groups = document.querySelectorAll(".nav-group");
    search.addEventListener("input", function () {
      var q = search.value.trim().toLowerCase();
      groups.forEach(function (group) {
        var visible = 0;
        group.querySelectorAll(".nav-item").forEach(function (item) {
          var hit = !q || item.innerText.toLowerCase().indexOf(q) > -1;
          item.style.display = hit ? "" : "none";
          if (hit) visible += 1;
        });
        group.style.display = visible ? "" : "none";
        group.classList.toggle("filtered", Boolean(q) && visible > 0);
      });
    });
    search.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        search.value = "";
        search.dispatchEvent(new Event("input"));
        search.blur();
      }
      if (e.key === "Enter") {
        var first = document.querySelector('.nav-group:not([style*="display: none"]) .nav-item');
        var href = first && first.getAttribute("href");
        if (href) window.location.href = href;
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== search &&
          !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
        e.preventDefault();
        search.focus();
      }
    });
  }

  /* 5. 移动端目录抽屉 */
  var toggle = document.getElementById("nav-toggle");
  var sidebar = document.getElementById("sidebar");
  if (toggle && sidebar) {
    toggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
    });
    sidebar.addEventListener("click", function (e) {
      if (e.target.closest(".nav-item")) sidebar.classList.remove("open");
    });
  }

  /* 6. 本章目录折叠 */
  var outToggle = document.getElementById("outline-toggle");
  var outline = document.getElementById("outline");
  if (outToggle && outline) {
    outToggle.addEventListener("click", function () {
      var collapsed = outline.classList.toggle("collapsed");
      outToggle.textContent = collapsed ? "展开" : "收起";
    });
  }

  /* 7. 滚动淡入动效 */
  (function () {
    var prefersReduced = window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var targets = document.querySelectorAll(
      ".section > h2, .formula, .code, .callout, .card, " +
      ".map-col, .stat, .takeaway, .pit, .tbl-wrap"
    );
    if (!targets.length || prefersReduced) return;

    targets.forEach(function (el, i) {
      el.classList.add("reveal");
      el.style.transitionDelay = Math.min(i % 4, 3) * 60 + "ms";
    });

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.classList.add("in");
            io.unobserve(en.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    targets.forEach(function (el) { io.observe(el); });
  })();
})();

// Render the deployment banner, fill in the version switcher, and navigate on either switcher's change event.
//
// Not part of the Grunt build: edit this file in place.
//
// The page's URL, not the `branch` setting, decides which version the reader is on, because one version is served
// from more than one directory: `latest` is a symlink to the current version's directory.
(async () => {
  const element = document.getElementById("oc-switchers-config");
  if (!element) {
    return;
  }
  const config = JSON.parse(element.textContent);

  // The last component of a directory URL's path.
  const basename = (url) => url.pathname.split("/").filter(Boolean).pop() || "";

  // `urlRoot` is this page's path to the root of its language's documentation.
  const languageRoot = new URL(config.urlRoot || "", location.href);
  const versionRoot = new URL("../", languageRoot);
  const documentationRoot = new URL("../", versionRoot);

  const language = basename(languageRoot) || config.language;
  const branch = basename(versionRoot) || config.branch;
  const path = location.pathname.startsWith(languageRoot.pathname)
    ? location.pathname.slice(languageRoot.pathname.length)
    : "";

  // Go to the first URL that exists, or to the last URL if none do.
  async function navigate(urls) {
    for (const url of urls.slice(0, -1)) {
      try {
        if ((await fetch(url, { method: "HEAD" })).ok) {
          location.assign(url);
          return;
        }
      } catch {
        // Try the next URL.
      }
    }
    location.assign(urls[urls.length - 1]);
  }

  // The `value` attribute is absent from the "Version" and "Language" placeholder options.
  function onChange(selector, callback) {
    const select = document.querySelector(`${selector} select`);
    select?.addEventListener("change", function () {
      const option = this.selectedOptions[0];
      if (option?.hasAttribute("value")) {
        callback(option.value);
      }
    });
    return select;
  }

  function addBanner(container, text, url, linkText) {
    container.classList.add("oc-fixed-alert-header");
    container.append(text);
    if (url) {
      const link = document.createElement("a");
      link.href = url;
      link.textContent = linkText;
      container.append(" ", link);
    }
  }

  onChange(".oc-language-switcher", (code) => {
    const root = new URL(`${code}/`, versionRoot);
    navigate([new URL(path, root).href, root.href]);
  });

  // Only the banner and the version switcher need versions.json.
  if (!config.versionsUrl) {
    return;
  }

  let data;
  try {
    const response = await fetch(new URL(config.versionsUrl, versionRoot));
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }
    data = await response.json();
  } catch (error) {
    // Leave the page without a banner and without a version switcher.
    console.warn(`Can't use ${config.versionsUrl}: ${error.message}`);
    return;
  }

  const versions = data.versions || [];
  const current = versions[0];
  const banner = document.querySelector(".oc-banner");

  if (banner && data.staging) {
    addBanner(banner, config.messages.staging, data.live_url, config.messages.stagingLink);
  } else if (banner && current && branch !== current.ref && versions.some((version) => version.ref === branch)) {
    const url = new URL(`${current.ref}/${language}/`, documentationRoot).href;
    addBanner(banner, config.messages.old, url, config.messages.oldLink.replace("%(version)s", current.label));
  }

  const select = onChange(".oc-version-switcher", (ref) => {
    const root = new URL(`${ref}/`, documentationRoot);
    navigate([new URL(`${language}/${path}`, root).href, new URL(`${language}/`, root).href, root.href]);
  });
  if (!select || !versions.length) {
    return;
  }

  for (const version of versions) {
    const option = document.createElement("option");
    option.value = version.ref;
    option.textContent = version.label;
    select.append(option);
  }

  // `.oc-switchers form` sets `display`, which overrides the hidden attribute.
  select.form.style.display = "";
})();

// Render the deployment banner and the version switcher's options, and make both switchers navigate client-side.
//
// This file is not part of the Grunt build. Edit it in place.
//
// The page's own URL is the source of truth for which version and language the reader is on, because one version can
// be served from more than one directory (`latest` is a symlink to the current version's directory). The `branch` and
// `language` settings are fallbacks, for a build that is served outside the deployed directory layout.
(() => {
  const element = document.getElementById("oc-switchers-config");
  if (!element) {
    return;
  }
  const config = JSON.parse(element.textContent);

  // The last path component of a directory URL.
  function basename(url) {
    const components = url.pathname.split("/").filter(Boolean);
    return components.length ? components[components.length - 1] : "";
  }

  // `urlRoot` is the relative path from this page to the root of this language's documentation.
  const languageRoot = new URL(config.urlRoot || "", location.href);
  const versionRoot = new URL("../", languageRoot);
  const documentationRoot = new URL("../", versionRoot);

  const language = basename(languageRoot) || config.language;
  const branch = basename(versionRoot) || config.branch;
  const path = location.pathname.startsWith(languageRoot.pathname)
    ? location.pathname.slice(languageRoot.pathname.length)
    : "";

  // Go to the first URL that exists, or to the last URL if none do.
  function navigate(urls) {
    const attempt = (index) => {
      if (index === urls.length - 1) {
        location.assign(urls[index]);
        return;
      }
      fetch(urls[index], { method: "HEAD" }).then(
        (response) => (response.ok ? location.assign(urls[index]) : attempt(index + 1)),
        () => attempt(index + 1),
      );
    };
    attempt(0);
  }

  // Switch on the selected option's `value` attribute, to ignore the "Version" and "Language" placeholder options.
  function onChange(select, callback) {
    select.addEventListener("change", function () {
      const option = this.selectedOptions[0];
      if (option?.hasAttribute("value")) {
        callback(option.value);
      }
    });
  }

  function addBanner(text, url, linkText) {
    const container = document.querySelector(".oc-banner");
    if (!container) {
      return;
    }
    container.classList.add("oc-fixed-alert-header");
    container.append(text);
    if (url) {
      const link = document.createElement("a");
      link.href = url;
      link.textContent = linkText;
      container.append(" ", link);
    }
  }

  const languageSelect = document.querySelector(".oc-language-switcher select");
  if (languageSelect) {
    onChange(languageSelect, (value) => {
      const root = new URL(`${value}/`, versionRoot);
      navigate([new URL(path, root).href, root.href]);
    });
  }

  // Only the version switcher and the deployment banner need versions.json.
  if (!config.versionsUrl) {
    return;
  }

  fetch(new URL(config.versionsUrl, versionRoot))
    .then((response) => {
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      return response.json();
    })
    .then((data) => {
      const versions = data.versions || [];
      // The first version is the current version.
      const current = versions[0];

      if (data.staging) {
        addBanner(config.messages.staging, data.live_url, config.messages.stagingLink);
      } else if (current && branch !== current.ref && versions.some((version) => version.ref === branch)) {
        addBanner(
          config.messages.old,
          new URL(`${current.ref}/${language}/`, documentationRoot).href,
          config.messages.oldLink.replace("%(version)s", current.label),
        );
      }

      const form = document.querySelector(".oc-version-switcher");
      const select = form?.querySelector("select");
      if (!select || !versions.length) {
        return;
      }

      for (const version of versions) {
        const option = document.createElement("option");
        option.value = version.ref;
        option.textContent = version.label;
        select.append(option);
      }

      onChange(select, (value) => {
        const root = new URL(`${value}/`, documentationRoot);
        navigate([new URL(`${language}/${path}`, root).href, new URL(`${language}/`, root).href, root.href]);
      });

      form.style.display = "";
    })
    // Leave the page as-is: no banner, and no version switcher.
    .catch((error) => console.warn(`Can't use ${config.versionsUrl}: ${error.message}`));
})();

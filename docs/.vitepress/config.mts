import { defineConfig } from "vitepress";

const vitePressConfigs = {
  srcDir: "src",
  title: "thin-ops AI Documentation",
  description: "Open source FinOps platform documentation",
  base: "/docs/",

  sitemap: {
    hostname: "https://narev.ai",
    lastmodDateOnly: false,
    transformItems: (items) => {
      return items.filter((item) => !item.url.includes("draft"));
    },
  },

  themeConfig: {
    search: {
      provider: "local" as const,
    },

    nav: [
      { text: "Getting Started", link: "/" },
      { text: "Connect Providers", link: "/connect-providers/" },
      { text: "FOCUS Specification", link: "/focus-specification" },
    ],

    sidebar: [
      {
        text: "Getting Started",
        items: [
          { text: "Introduction", link: "/" },
          { text: "Deployment", link: "/getting-started/deployment" },
          { text: "Sync Providers", link: "/getting-started/sync-providers" },
        ],
      },
      {
        text: "Connect Providers",
        items: [
          { text: "Overview", link: "/connect-providers/" },
          { text: "AWS", link: "/connect-providers/aws" },
          { text: "Azure", link: "/connect-providers/azure" },
          { text: "Google Cloud Platform", link: "/connect-providers/gcp" },
          { text: "OpenAI", link: "/connect-providers/openai" },
        ],
      },
      {
        text: "FOCUS Specification",
        items: [
          { text: "FOCUS 1.2 Overview", link: "/focus-specification" },
        ],
      },
    ],

    socialLinks: [{ icon: "github", link: "https://github.com/narevai/thin-ops" }],

    editLink: {
      pattern:
        "https://github.com/narevai/thin-ops/issues/new?title=Documentation%20feedback:%20:path&body=**Page:**%20https://narev.ai/:path%0A%0A**Feedback:**%0A%0A<!-- Please describe your feedback about this documentation page -->",
      text: "❓ Something unclear?",
    },
  },
};

export default defineConfig(vitePressConfigs);

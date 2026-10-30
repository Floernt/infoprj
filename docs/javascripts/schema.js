/**
 * Injects JSON-LD structured data (Schema.org) for GEO/SEO.
 * - WebSite schema on all pages
 * - FAQPage schema on pages containing FAQ sections
 * (BreadcrumbList : voir overrides/main.html)
 */
(function () {
  var BASE_URL = "https://infoprj.be";
  var SITE_NAME = "La réorganisation judiciaire en Belgique";
  var AUTHOR = "Florian Ernotte";

  function injectSchema(schema) {
    var script = document.createElement("script");
    script.type = "application/ld+json";
    script.textContent = JSON.stringify(schema);
    document.head.appendChild(script);
  }

  // 1. WebSite schema (all pages)
  injectSchema({
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": SITE_NAME,
    "url": BASE_URL,
    "description": "Guide pratique de la procédure de réorganisation judiciaire (PRJ) en Belgique : PRJ publique et privée, sursis, plan, classes de créanciers, rôle du dirigeant, des créanciers et des professionnels du chiffre. Basé sur le Livre XX du Code de droit économique.",
    "inLanguage": "fr-BE",
    "author": {
      "@type": "Person",
      "name": AUTHOR
    },
    "publisher": {
      "@type": "Organization",
      "name": "Info-PRJ",
      "url": BASE_URL
    }
  });

  // 2. LegalService schema (all pages)
  injectSchema({
    "@context": "https://schema.org",
    "@type": "LegalService",
    "name": SITE_NAME,
    "url": BASE_URL,
    "description": "Ressource juridique de référence sur la procédure de réorganisation judiciaire en Belgique",
    "inLanguage": "fr-BE",
    "areaServed": {
      "@type": "Country",
      "name": "Belgique"
    },
    "knowsAbout": [
      "Réorganisation judiciaire en Belgique",
      "Livre XX du Code de droit économique",
      "Entreprises en difficulté",
      "Plan de réorganisation",
      "Classes de créanciers",
      "Chambre des entreprises en difficulté",
      "Transfert sous autorité de justice"
    ]
  });

  // 3. Article schema (page-specific)
  var pageTitle = document.querySelector("h1");
  var pageDescription = document.querySelector('meta[name="description"]');
  if (pageTitle && pageDescription) {
    injectSchema({
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": pageTitle.textContent.trim(),
      "description": pageDescription.getAttribute("content"),
      "url": window.location.href,
      "inLanguage": "fr-BE",
      "author": {
        "@type": "Person",
        "name": AUTHOR
      },
      "publisher": {
        "@type": "Organization",
        "name": "Info-PRJ",
        "url": BASE_URL
      },
      "isPartOf": {
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": BASE_URL
      }
    });
  }

  // 4. FAQPage schema — auto-extracted from Q&A sections
  var headings = document.querySelectorAll("h3");
  var faqItems = [];

  headings.forEach(function (h) {
    var text = h.textContent.trim();
    // Detect question patterns
    if (text.match(/^(Puis-je|Peut-on|Comment|Qu'est|Que faire|Combien|Quand|Y a-t-il|Est-ce|Faut-il|Dois-je)/i)) {
      var answer = "";
      var sibling = h.nextElementSibling;
      while (sibling && sibling.tagName !== "H3" && sibling.tagName !== "H2") {
        answer += sibling.textContent.trim() + " ";
        sibling = sibling.nextElementSibling;
      }
      if (answer.trim().length > 20) {
        faqItems.push({
          "@type": "Question",
          "name": text,
          "acceptedAnswer": {
            "@type": "Answer",
            "text": answer.trim().substring(0, 500)
          }
        });
      }
    }
  });

  if (faqItems.length > 0) {
    injectSchema({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": faqItems
    });
  }

  // Le BreadcrumbList est produit côté serveur par overrides/main.html,
  // avec les libellés du menu, pour les robots qui n'exécutent pas JavaScript.
})();

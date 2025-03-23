# Schema Markup Implementation Guide for Kriangle

## Overview

This document provides technical details about the schema markup implementation on the Kriangle website. Schema markup helps search engines understand your website content better, potentially improving search visibility through rich snippets and enhanced search features.

## Schema Types Implemented

The following schema.org types have been implemented across the Kriangle website:

1. Organization
2. WebPage (and specific types like AboutPage)
3. Service
4. ItemList
5. Blog
6. BlogPosting (for individual blog posts)

## Base Organization Schema

The `Organization` schema is implemented site-wide in the base template:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Kriangle",
  "url": "https://kriangle.com",
  "logo": "https://kriangle.com/static/images/logo.png",
  "description": "Kriangle provides expert website development and SEO services for small businesses worldwide.",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+01 8483599697",
    "contactType": "customer service",
    "email": "info@kriangle.com"
  },
  "sameAs": [
    "https://www.facebook.com/krishna.dhakal.37",
    "https://www.linkedin.com/in/krishnadhakal/",
    "https://www.instagram.com/cris_nadhakal/"
  ]
}
</script>
```

This provides search engines with basic information about the company, including contact details and social profiles.

## Page-Specific Schema

### Homepage

The homepage includes the base Organization schema with additional WebPage information:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "Professional Website Development & SEO Services",
  "description": "Kriangle offers professional website development and SEO services to help businesses grow online.",
  "publisher": {
    "@type": "Organization",
    "name": "Kriangle",
    "logo": {
      "@type": "ImageObject",
      "url": "https://kriangle.com/static/images/logo.png"
    }
  },
  "mainEntity": {
    "@type": "WebSite",
    "name": "Kriangle",
    "url": "https://kriangle.com"
  }
}
</script>
```

### About Page

The About page uses the AboutPage schema type:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "AboutPage",
  "mainEntity": {
    "@type": "Organization",
    "name": "Kriangle",
    "description": "Kriangle is led by an experienced full-stack developer with over 13 years in software development, specializing in website development and SEO services.",
    "foundingDate": "2021",
    "founder": {
      "@type": "Person",
      "name": "Krishna Dhakal"
    }
  }
}
</script>
```

### Services Page

The Services page uses an ItemList schema to organize the various services offered:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "item": {
          "@type": "Service",
          "name": "SEO Optimization",
          "description": "Comprehensive SEO services including on-page and off-page optimization to improve search engine rankings.",
          "provider": {
            "@type": "Organization",
            "name": "Kriangle"
          }
        }
      },
      {
        "@type": "ListItem",
        "position": 2,
        "item": {
          "@type": "Service",
          "name": "Full-Stack Python Django Development",
          "description": "Custom web application development using Python Django framework.",
          "provider": {
            "@type": "Organization",
            "name": "Kriangle"
          }
        }
      },
      {
        "@type": "ListItem",
        "position": 3,
        "item": {
          "@type": "Service",
          "name": "WordPress Management",
          "description": "Expert WordPress management, customization and optimization.",
          "provider": {
            "@type": "Organization",
            "name": "Kriangle"
          }
        }
      }
    ]
  }
}
</script>
```

### Blog Page

The Blog page implements the Blog schema:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Blog",
  "name": "Kriangle Web Development & SEO Blog",
  "description": "Expert insights and tips on website development, SEO, and web applications.",
  "url": "https://kriangle.com/blog/",
  "publisher": {
    "@type": "Organization",
    "name": "Kriangle",
    "logo": {
      "@type": "ImageObject",
      "url": "https://kriangle.com/static/images/logo.png"
    }
  }
}
</script>
```

### Blog Posts

For individual blog posts, the BlogPosting schema is used:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "How to Optimize Your Website for Search Engines in 2025",
  "image": "https://kriangle.com/static/images/SEO_Services.png",
  "datePublished": "2025-03-22",
  "dateModified": "2025-03-22",
  "author": {
    "@type": "Person",
    "name": "Krishna Dhakal"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Kriangle",
    "logo": {
      "@type": "ImageObject",
      "url": "https://kriangle.com/static/images/logo.png"
    }
  },
  "description": "Search engine optimization (SEO) has evolved significantly in 2025. Learn the latest techniques to improve your website's search rankings."
}
</script>
```

## BreadcrumbList Schema

Breadcrumb navigation is enhanced with BreadcrumbList schema:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://kriangle.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Services",
      "item": "https://kriangle.com/services/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "SEO Services",
      "item": "https://kriangle.com/services/seo/"
    }
  ]
}
</script>
```

## Local Business Schema

For local business targeting, LocalBusiness schema is implemented:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Kriangle",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main Street",
    "addressLocality": "Anytown",
    "addressRegion": "NY",
    "postalCode": "10001",
    "addressCountry": "US"
  },
  "telephone": "+01 8483599697",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "17:00"
    }
  ]
}
</script>
```

## FAQ Schema

For the FAQ section on service pages:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What SEO services does Kriangle offer?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Kriangle offers comprehensive SEO services including on-page optimization, off-page link building, technical SEO audits, content optimization, and ongoing SEO management."
      }
    },
    {
      "@type": "Question",
      "name": "Do you develop custom web applications?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, we specialize in developing custom web applications using Python Django framework. Our applications are tailored to your specific business needs and are fully scalable."
      }
    }
  ]
}
</script>
```

## Best Practices Implemented

1. **Nested Schema Integration**
   - Organization schema embedded within other schema types
   - Proper linking between related schemas

2. **Consistent Properties**
   - Consistent use of name, description, and URL properties
   - Proper image references with full URLs

3. **Schema Validation**
   - All schema has been validated using Google's Rich Results Test
   - Potential errors or warnings addressed

4. **Dynamic Schema Generation**
   - Schema is generated using Django template variables
   - Content updates automatically reflected in schema

## Testing and Validation

All schema markup has been tested using:

1. **Google's Rich Results Test**
   - URL: https://search.google.com/test/rich-results
   - All pages pass validation without errors

2. **Schema.org Validator**
   - URL: https://validator.schema.org/
   - No critical errors detected

## Implementation in Django Templates

Schema markup is implemented in the Django templates using the `{% block additional_schema %}` approach:

```html
{% block additional_schema %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  ...
}
</script>
{% endblock %}
```

This allows each template to define its specific schema while inheriting the base Organization schema.

## Monitoring and Future Enhancements

1. **Google Search Console Monitoring**
   - Track rich result impressions and click-through rates
   - Identify enhancement opportunities

2. **Planned Enhancements**
   - Add Product schema for e-commerce products
   - Implement HowTo schema for tutorial content
   - Add JobPosting schema for career opportunities

## References

1. Schema.org Documentation: https://schema.org/docs/schemas.html
2. Google Structured Data Guidelines: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
3. JSON-LD Syntax Guide: https://json-ld.org/playground/

---

Document prepared by Kriangle SEO Team  
Last updated: March 22, 2025 
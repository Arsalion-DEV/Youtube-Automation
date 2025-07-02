# Scout Next Template

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app) and configured with TailwindCSS v4 and ShadCN UI.

## Getting Started

First, run the development server:

```bash
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

## Project Configuration

### Package Management

This project uses [Bun](https://bun.sh/) as the package manager:

- Install dependencies: `bun add <package-name>`
- Run scripts: `bun <script-name>`
- Manage dev dependencies: `bun add -d <package-name>`

### Theme Customization

The project uses Tailwind CSS V4 with a theme defined in:

- `app/globals.css` - For CSS variables including colors in OKLCH format and custom theming
- Tailwind V4 uses the new `@theme` directive for configuration

### ShadCN UI Components

This project uses [ShadCN UI](https://ui.shadcn.com) for styled components. The components are incorporated directly into the codebase (not as dependencies), making them fully customizable. All components have been installed:

- accordion
- alert-dialog
- alert
- aspect-ratio
- avatar
- badge
- breadcrumb
- button
- calendar
- card
- carousel
- chart
- checkbox
- collapsible
- command
- context-menu
- dialog
- drawer
- dropdown-menu
- form
- hover-card
- input-otp
- input
- label
- menubar
- navigation-menu
- pagination
- popover
- progress
- radio-group
- scroll-area
- select
- separator
- sheet
- skeleton
- slider
- sonner
- switch
- table
- tabs
- textarea
- toast
- toggle-group
- toggle

### Icon Library

[Lucide React](https://lucide.dev/) is the preferred icon library for this project, as specified in components.json. Always use Lucide icons to maintain consistency:

```tsx
import { ArrowRight } from "lucide-react";

// Use in components
<Button>
  <span>Click me</span>
  <ArrowRight />
</Button>;
```

### Font Configuration

This project uses [Next.js Font Optimization](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) with:

- Inter (sans-serif)
- Playfair Display (serif)

To change or update fonts:

1. Modify `app/layout.tsx` to import and configure the desired fonts:

```tsx
import { NewFont } from "next/font/google";

const newFont = NewFont({
  variable: "--font-new-font",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
});

<body className={`${newFont.variable} antialiased`}>
```

2. Update the font family in `app/globals.css`:

```css
--font-sans: var(--font-new-font);
```

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

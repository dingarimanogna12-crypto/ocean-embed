This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Deploying predictions

The prediction API runs the Python model as a separate FastAPI service; Vercel
serves the Next.js frontend and proxies prediction requests to that service.
The app defaults to `https://ocean-embed-8int.onrender.com`, so no Vercel
environment variable is required for the current Render service.

1. Create a Render Blueprint from this repository using `render.yaml`. The
   blueprint deploys the service from `backend/`.
2. If using a different Render service, set `OCEANEMBED_API_URL` in Vercel
   Production and Preview to its base URL, without a trailing `/predict`.
3. Redeploy Vercel after changing the URL or environment variable.

The first prediction after a free Render service has been idle may take longer
while Render wakes the service.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

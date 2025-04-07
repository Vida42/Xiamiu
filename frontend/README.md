# Xiamiu Music Frontend

A Next.js-based frontend for the Xiamiu music database, featuring artists, albums, songs, and genres.

## Features

- **Responsive design** that works on desktop and mobile
- **Artists, Albums, Songs, and Genres pages** with details and related items
- **Search functionality** to find music content quickly

## Getting Started

### Prerequisites

- Node.js 14+ and npm/yarn

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

## Key Pages

- `/` - Home page with featured content
- `/artists` - List of all artists
- `/artists/[id]` - Details page for a specific artist
- `/albums` - List of all albums
- `/albums/[id]` - Details page for a specific album
- `/songs` - List of all songs
- `/songs/[id]` - Details page for a specific song
- `/genres` - List of all genres
- `/genres/[id]` - Details page for a specific genre
- `/search` - Search results page

## Backend Connection

The frontend connects to the FastAPI backend via an API proxy set up in the `next.config.js` file. All API requests go through the `/api` route which is proxied to the backend service.

### API Structure

The frontend uses the `api.js` utility to make requests to the backend, with functions for each entity type (artists, albums, songs, genres).

## Folder Structure

- `/pages` - Next.js pages (routes)
- `/components` - Reusable React components
- `/utils` - Utility functions (like API calls)
- `/public` - Static assets (images, etc.)

## Deployment

This is a Next.js application that can be deployed to platforms like Vercel, Netlify, or any hosting provider that supports Node.js applications.

```bash
# Build for production
npm run build

# Start production server
npm run start
``` 
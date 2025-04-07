import axios from 'axios';

const API_URL = '/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for logging or auth tokens if needed
apiClient.interceptors.request.use(
  config => {
    console.log(`Making request to: ${config.url}`);
    return config;
  },
  error => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('Response error:', error);
    // You can add custom error handling here
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.log('Error data:', error.response.data);
      console.log('Error status:', error.response.status);
    } else if (error.request) {
      // The request was made but no response was received
      console.log('No response received:', error.request);
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Search
  search: async (query) => {
    try {
      const response = await apiClient.get(`/search/?query=${query}`);
      return response.data;
    } catch (error) {
      console.error("Error searching:", error);
      throw error;
    }
  },

  // Artists
  getArtists: async () => {
    try {
      const response = await apiClient.get('/artists/');
      return response.data;
    } catch (error) {
      console.error("Error fetching artists:", error);
      throw error;
    }
  },
  getArtist: async (id) => {
    try {
      const response = await apiClient.get(`/artists/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching artist ${id}:`, error);
      throw error;
    }
  },
  getArtistAlbums: async (id) => {
    try {
      const response = await apiClient.get(`/artists/${id}/albums`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching albums for artist ${id}:`, error);
      throw error;
    }
  },
  getArtistMeta: async (id) => {
    try {
      const response = await apiClient.get(`/artists/${id}/meta`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching metadata for artist ${id}:`, error);
      throw error;
    }
  },
  getArtistComments: async (id) => {
    try {
      const response = await apiClient.get(`/artists/${id}/comments`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching comments for artist ${id}:`, error);
      throw error;
    }
  },

  // Albums
  getAlbums: async () => {
    try {
      const response = await apiClient.get('/albums/');
      return response.data;
    } catch (error) {
      console.error("Error fetching albums:", error);
      throw error;
    }
  },
  getAlbum: async (id) => {
    try {
      const response = await apiClient.get(`/albums/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching album ${id}:`, error);
      throw error;
    }
  },
  getAlbumSongs: async (id) => {
    try {
      const response = await apiClient.get(`/albums/${id}/songs`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching songs for album ${id}:`, error);
      throw error;
    }
  },
  getAlbumMeta: async (id) => {
    try {
      const response = await apiClient.get(`/albums/${id}/meta`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching metadata for album ${id}:`, error);
      throw error;
    }
  },
  getAlbumComments: async (id) => {
    try {
      const response = await apiClient.get(`/albums/${id}/comments`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching comments for album ${id}:`, error);
      throw error;
    }
  },

  // Songs
  getSongs: async () => {
    try {
      const response = await apiClient.get('/songs/');
      return response.data;
    } catch (error) {
      console.error("Error fetching songs:", error);
      throw error;
    }
  },
  getSong: async (id) => {
    try {
      const response = await apiClient.get(`/songs/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching song ${id}:`, error);
      throw error;
    }
  },
  getSongMeta: async (id) => {
    try {
      const response = await apiClient.get(`/songs/${id}/meta`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching metadata for song ${id}:`, error);
      throw error;
    }
  },
  getSongComments: async (id) => {
    try {
      const response = await apiClient.get(`/songs/${id}/comments`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching comments for song ${id}:`, error);
      throw error;
    }
  },

  // Genres
  getGenres: async () => {
    try {
      const response = await apiClient.get('/genres/');
      return response.data;
    } catch (error) {
      console.error("Error fetching genres:", error);
      throw error;
    }
  },
  getGenre: async (id) => {
    try {
      const response = await apiClient.get(`/genres/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching genre ${id}:`, error);
      throw error;
    }
  },

  // Users
  getUsers: async () => {
    try {
      const response = await apiClient.get('/users/');
      return response.data;
    } catch (error) {
      console.error("Error fetching users:", error);
      throw error;
    }
  },
  getUser: async (id) => {
    try {
      const response = await apiClient.get(`/users/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching user ${id}:`, error);
      throw error;
    }
  },
}; 
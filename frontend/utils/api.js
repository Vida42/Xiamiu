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
    
    // Add token to requests if user is logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
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
      
      // If unauthorized and not already on login page, redirect to login
      if (error.response.status === 401 && window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.log('No response received:', error.request);
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Authentication
  login: async (username, password) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await axios.post(`${API_URL}/token`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      localStorage.setItem('access_token', response.data.access_token);
      return response.data;
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
  },
  
  getCurrentUser: async () => {
    try {
      const response = await apiClient.get('/users/me');
      return response.data;
    } catch (error) {
      console.error("Error fetching current user:", error);
      throw error;
    }
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
  
  getUserSongComments: async (userId) => {
    try {
      const response = await apiClient.get(`/users/${userId}/comments/songs`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching song comments for user ${userId}:`, error);
      throw error;
    }
  },
  
  getUserArtistComments: async (userId) => {
    try {
      const response = await apiClient.get(`/users/${userId}/comments/artists`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching artist comments for user ${userId}:`, error);
      throw error;
    }
  },
  
  getUserAlbumComments: async (userId) => {
    try {
      const response = await apiClient.get(`/users/${userId}/comments/albums`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching album comments for user ${userId}:`, error);
      throw error;
    }
  },

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
  getArtistsByReign: async (reign) => {
    try {
      const response = await apiClient.get(`/artists/reign/${reign}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching artists by reign ${reign}:`, error);
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
  getAlbumsByLanguage: async (language) => {
    try {
      const response = await apiClient.get(`/albums/language/${language}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching albums by language ${language}:`, error);
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
  getArtistsByGenre: async (id) => {
    try {
      const response = await apiClient.get(`/genres/${id}/artists`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching artists for genre ${id}:`, error);
      throw error;
    }
  },
  getAlbumsByGenre: async (id) => {
    try {
      const response = await apiClient.get(`/genres/${id}/albums`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching albums for genre ${id}:`, error);
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
  }
};
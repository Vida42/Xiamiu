import { useEffect, useState } from 'react';
import { Heading, Text, SimpleGrid, Box, Flex, Input, InputGroup, InputLeftElement, Select } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { AlbumCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';
import { SearchIcon } from '@chakra-ui/icons';

export default function Albums() {
  const [albums, setAlbums] = useState([]);
  const [filteredAlbums, setFilteredAlbums] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name');

  useEffect(() => {
    const fetchAlbums = async () => {
      try {
        setIsLoading(true);
        const data = await api.getAlbums();
        setAlbums(data);
        setFilteredAlbums(data);
      } catch (err) {
        console.error('Error fetching albums:', err);
        setError('Failed to load albums. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAlbums();
  }, []);

  useEffect(() => {
    let result = [...albums];
    
    // Filter by search term
    if (searchTerm.trim()) {
      result = result.filter(album => 
        album.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Sort results
    switch (sortBy) {
      case 'name':
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'release_date_newest':
        result.sort((a, b) => new Date(b.release_date) - new Date(a.release_date));
        break;
      case 'release_date_oldest':
        result.sort((a, b) => new Date(a.release_date) - new Date(b.release_date));
        break;
      case 'rating':
        result.sort((a, b) => b.star - a.star);
        break;
      default:
        break;
    }
    
    setFilteredAlbums(result);
  }, [searchTerm, sortBy, albums]);

  const renderContent = () => {
    if (error) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Error</Heading>
          <Text>{error}</Text>
        </Box>
      );
    }
  
    return (
      <Box>
        <Heading mb={6}>Albums</Heading>
        
        <Flex 
          direction={{ base: 'column', md: 'row' }} 
          gap={4} 
          mb={8} 
          justifyContent="space-between"
          alignItems={{ base: 'stretch', md: 'center' }}
        >
          <InputGroup maxW={{ base: '100%', md: '500px' }}>
            <InputLeftElement pointerEvents="none">
              <SearchIcon color="gray.300" />
            </InputLeftElement>
            <Input 
              placeholder="Filter albums by name..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
          
          <Select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            maxW={{ base: '100%', md: '200px' }}
          >
            <option value="name">Name (A-Z)</option>
            <option value="release_date_newest">Newest First</option>
            <option value="release_date_oldest">Oldest First</option>
            <option value="rating">Highest Rated</option>
          </Select>
        </Flex>
  
        {isLoading ? (
          <Flex justify="center" py={10}>
            <Text>Loading albums...</Text>
          </Flex>
        ) : filteredAlbums.length === 0 ? (
          <Box textAlign="center" py={10}>
            <Text>No albums found matching "{searchTerm}"</Text>
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            {filteredAlbums.map(album => (
              <AlbumCard key={album.album_id} album={album} />
            ))}
          </SimpleGrid>
        )}
      </Box>
    );
  };

  return (
    <XiamiuLayout>
      {renderContent()}
    </XiamiuLayout>
  );
} 
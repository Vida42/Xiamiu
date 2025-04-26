import { useEffect, useState } from 'react';
import { Heading, Text, SimpleGrid, Box, Flex, Link, Grid, GridItem, VStack, Divider, Select } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { ArtistCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';

export default function Artists() {
  const [artists, setArtists] = useState([]);
  const [filteredArtists, setFilteredArtists] = useState([]);
  const [genres, setGenres] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFilterLoading, setIsFilterLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('popular');
  const [activeGenre, setActiveGenre] = useState(null);
  const [sortBy, setSortBy] = useState('name');
  const [page, setPage] = useState(1);
  const itemsPerPage = 8;
  
  const artistFilters = [
    { id: 'popular', label: '热门' },
    { id: 'China', label: '中国' },
    { id: 'United States of America', label: '美国' },
    { id: 'United Kingdom', label: '英国' },
    { id: 'Japan', label: '日本' },
    { id: 'Korea', label: '韩国' },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // Fetch artists
        const artistsData = await api.getArtists();
        setArtists(artistsData);
        
        // Fetch genres
        const genresData = await api.getGenres();
        setGenres(genresData);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    let isMounted = true;
    setIsFilterLoading(true);
    
    // Filter by region (country/region)
    if (activeFilter !== 'popular') {
      const fetchArtistsByRegion = async () => {
        try {
          const regionArtists = await api.getArtistsByRegion(activeFilter);
          
          if (!isMounted) return;
          
          // If also filtering by genre, filter the region results by genre
          if (activeGenre) {
            const fetchArtistsByGenre = async () => {
              try {
                const genreArtists = await api.getArtistsByGenre(activeGenre);
                
                if (!isMounted) return;
                
                // Intersection of region artists and genre artists
                const artistIds = new Set(genreArtists.map(artist => artist.artist_id));
                const filtered = regionArtists.filter(artist => artistIds.has(artist.artist_id));
                applySort(filtered);
                setIsFilterLoading(false);
              } catch (err) {
                console.error(`Error fetching artists for genre ${activeGenre}:`, err);
                if (isMounted) {
                  applySort(regionArtists);
                  setIsFilterLoading(false);
                }
              }
            };
            
            fetchArtistsByGenre();
          } else {
            applySort(regionArtists);
            setIsFilterLoading(false);
          }
        } catch (err) {
          console.error(`Error fetching artists for region ${activeFilter}:`, err);
          if (isMounted) {
            applySort([]);
            setError(`Failed to load ${activeFilter} artists. Please try again later.`);
            setIsFilterLoading(false);
          }
        }
      };
      
      fetchArtistsByRegion();
    } else {
      // For "popular" tab, show artists with highest popularity
      // For this demo, we'll just sort by name as a placeholder
      let result = [...artists];
      
      // Filter by genre if selected
      if (activeGenre) {
        const fetchArtistsByGenre = async () => {
          try {
            const genreArtists = await api.getArtistsByGenre(activeGenre);
            
            if (!isMounted) return;
            
            // Intersection of all artists and genre artists
            const artistIds = new Set(genreArtists.map(artist => artist.artist_id));
            result = result.filter(artist => artistIds.has(artist.artist_id));
            applySort(result);
            setIsFilterLoading(false);
          } catch (err) {
            console.error(`Error fetching artists for genre ${activeGenre}:`, err);
            if (isMounted) {
              applySort(result);
              setIsFilterLoading(false);
            }
          }
        };
        
        fetchArtistsByGenre();
      } else {
        applySort(result);
        setIsFilterLoading(false);
      }
    }
    
    return () => {
      isMounted = false;
    };
  }, [activeFilter, activeGenre, sortBy, artists]);

  const applySort = (artistsToSort) => {
    let result = [...artistsToSort];
    
    // Sort results
    switch (sortBy) {
      case 'name':
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'region':
        result.sort((a, b) => a.region.localeCompare(b.region));
        break;
      default:
        break;
    }
    
    setFilteredArtists(result);
  };

  // Reset the page when filtered artists change
  useEffect(() => {
    setPage(1);
  }, [filteredArtists]);

  // Pagination logic
  const totalPages = Math.ceil(filteredArtists.length / itemsPerPage);
  const currentPageArtists = filteredArtists.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  );

  const handlePageChange = (newPage) => {
    setPage(newPage);
    window.scrollTo(0, 0);
  };

  const renderGenreList = () => {
    return (
      <VStack align="stretch" spacing={2} mb={6}>
        <Heading size="sm" mb={2}>音乐风格</Heading>
        <Box 
          as="div" 
          onClick={() => setActiveGenre(null)} 
          cursor="pointer" 
          p={2}
          bg={activeGenre === null ? "black" : "transparent"}
          color={activeGenre === null ? "white" : "inherit"}
          borderRadius="md"
          fontWeight={activeGenre === null ? "bold" : "normal"}
          _hover={{ bg: "#f70" }}
        >
          全部风格
        </Box>
        <Divider />
        {genres.map(genre => (
          <Box 
            key={genre.id} 
            as="div" 
            onClick={() => setActiveGenre(genre.id)} 
            cursor="pointer"
            p={2}
            bg={activeGenre === genre.id ? "black" : "transparent"}
            color={activeGenre === genre.id ? "white" : "inherit"}
            borderRadius="md"
            fontWeight={activeGenre === genre.id ? "bold" : "normal"}
            _hover={{ bg: "#f70" }}
          >
            {genre.name}
          </Box>
        ))}
      </VStack>
    );
  };

  const renderPagination = () => {
    if (totalPages <= 1) return null;
    
    return (
      <Flex mt={8} justify="center">
        <Flex as="ul" className="bottom-ul-menu">
          {page > 1 && (
            <Box as="li">
              <Link onClick={() => handlePageChange(page - 1)}>
                上一页
              </Link>
            </Box>
          )}
          {Array.from({ length: totalPages }, (_, i) => i + 1).map(pageNum => (
            <Box 
              as="li" 
              key={pageNum} 
              className={pageNum === page ? "active" : ""}
            >
              <Link onClick={() => handlePageChange(pageNum)}>
                {pageNum}
              </Link>
            </Box>
          ))}
          {page < totalPages && (
            <Box as="li">
              <Link onClick={() => handlePageChange(page + 1)}>
                下一页
              </Link>
            </Box>
          )}
        </Flex>
      </Flex>
    );
  };

  const renderContent = () => {
    if (error && !filteredArtists.length) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Error</Heading>
          <Text>{error}</Text>
        </Box>
      );
    }
  
    return (
      <Grid templateColumns={{ base: "1fr", md: "200px 1fr" }} gap={6}>
        {/* Left sidebar with genres */}
        <GridItem display={{ base: "none", md: "block" }}>
          {renderGenreList()}
        </GridItem>
        
        {/* Main content */}
        <GridItem>
          <Heading size="md" mb={6}>Artists</Heading>
          
          <Flex 
            direction={{ base: 'column', md: 'row' }} 
            gap={4} 
            mb={8} 
            justifyContent="space-between"
            alignItems={{ base: 'stretch', md: 'flex-start' }}
            className="artists-filter"
          >
            <Flex 
              as="ul" 
              className="bottom-ul-menu"
              mb={{ base: 4, md: 0 }}
              flex="1"
              overflowX={{ base: "auto", md: "visible" }}
            >
              {artistFilters.map(filter => (
                <Box 
                  as="li" 
                  key={filter.id} 
                  className={activeFilter === filter.id ? "active" : ""}
                >
                  <Link onClick={() => {
                    setActiveFilter(filter.id);
                    setPage(1); // Reset page when changing filter
                  }}>
                    {filter.label}
                  </Link>
                </Box>
              ))}
            </Flex>
          </Flex>
    
          {isLoading || isFilterLoading ? (
            <Flex justify="center" py={10}>
              <Text>Loading artists...</Text>
            </Flex>
          ) : currentPageArtists.length === 0 ? (
            <Box textAlign="center" py={10}>
              <Text>No artists found with the selected filters</Text>
            </Box>
          ) : (
            <>
              <Flex justify="space-between" mb={4} align="center">
                <Text fontSize="sm" color="gray.600">
                  Showing {(page - 1) * itemsPerPage + 1}-{Math.min(page * itemsPerPage, filteredArtists.length)} of {filteredArtists.length} artists
                </Text>
              </Flex>
              
              <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={3}>
                {currentPageArtists.map(artist => (
                  <ArtistCard key={artist.artist_id} artist={artist} />
                ))}
              </SimpleGrid>
              
              {renderPagination()}
            </>
          )}
        </GridItem>
      </Grid>
    );
  };

  return (
    <XiamiuLayout>
      {renderContent()}
    </XiamiuLayout>
  );
} 
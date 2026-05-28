import { useEffect, useState } from 'react';
import { Heading, Text, SimpleGrid, Box, Flex, Select, Link, Grid, GridItem, VStack, Divider } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { AlbumCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';
import { useLanguage } from '../../contexts/LanguageContext';

export default function Albums() {
  const { t } = useLanguage();
  const [albums, setAlbums] = useState([]);
  const [filteredAlbums, setFilteredAlbums] = useState([]);
  const [genres, setGenres] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFilterLoading, setIsFilterLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('popular');
  const [activeGenre, setActiveGenre] = useState(null);
  const [sortBy, setSortBy] = useState('name');
  const [page, setPage] = useState(1);
  const itemsPerPage = 8;
  
  const albumFilters = [
    { id: 'popular', label: t('popular') },
    { id: 'Mandarin', label: t('chinese') },
    { id: 'English', label: t('western') },
    { id: 'Japanese', label: t('japanese') },
    { id: 'Korean', label: t('korean') },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // Fetch albums
        const albumsData = await api.getAlbums();
        setAlbums(albumsData);
        
        // Fetch genres
        const genresData = await api.getGenres();
        setGenres(genresData);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(t('failedLoadData'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    let isMounted = true;
    setIsFilterLoading(true);
    
    let result = [...albums];
    
    // Filter by language
    if (activeFilter !== 'popular') {
      const fetchAlbumsByLanguage = async () => {
        try {
          const languageAlbums = await api.getAlbumsByLanguage(activeFilter);
          
          if (!isMounted) return;
          
          // If also filtering by genre, filter the language results by genre
          if (activeGenre) {
            const fetchAlbumsByGenre = async () => {
              try {
                const genreAlbums = await api.getAlbumsByGenre(activeGenre);
                
                if (!isMounted) return;
                
                // Intersection of language albums and genre albums
                const albumIds = new Set(genreAlbums.map(album => album.album_id));
                const filtered = languageAlbums.filter(album => albumIds.has(album.album_id));
                applySort(filtered);
                setIsFilterLoading(false);
              } catch (err) {
                console.error(`Error fetching albums for genre ${activeGenre}:`, err);
                if (isMounted) {
                  applySort(languageAlbums);
                  setIsFilterLoading(false);
                }
              }
            };
            
            fetchAlbumsByGenre();
          } else {
            applySort(languageAlbums);
            setIsFilterLoading(false);
          }
        } catch (err) {
          console.error(`Error fetching albums for language ${activeFilter}:`, err);
          if (isMounted) {
            applySort([]);
            setError(t('failedLoadData'));
            setIsFilterLoading(false);
          }
        }
      };
      
      fetchAlbumsByLanguage();
    } else {
      // For "popular" tab, show albums with highest star ratings
      result = [...albums].sort((a, b) => b.star - a.star);
      
      // Filter by genre if selected
      if (activeGenre) {
        const fetchAlbumsByGenre = async () => {
          try {
            const genreAlbums = await api.getAlbumsByGenre(activeGenre);
            
            if (!isMounted) return;
            
            // Intersection of popularity sorted albums and genre albums
            const albumIds = new Set(genreAlbums.map(album => album.album_id));
            result = result.filter(album => albumIds.has(album.album_id));
            applySort(result);
            setIsFilterLoading(false);
          } catch (err) {
            console.error(`Error fetching albums for genre ${activeGenre}:`, err);
            if (isMounted) {
              applySort(result);
              setIsFilterLoading(false);
            }
          }
        };
        
        fetchAlbumsByGenre();
      } else {
        applySort(result);
        setIsFilterLoading(false);
      }
    }
    
    return () => {
      isMounted = false;
    };
  }, [activeFilter, activeGenre, sortBy, albums]);

  const applySort = (albumsToSort) => {
    let result = [...albumsToSort];
    
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
  };

  // Reset the page when filtered albums change
  useEffect(() => {
    setPage(1);
  }, [filteredAlbums]);

  // Pagination logic
  const totalPages = Math.ceil(filteredAlbums.length / itemsPerPage);
  const currentPageAlbums = filteredAlbums.slice(
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
        <Heading size="sm" mb={2}>{t('musicStyles')}</Heading>
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
          {t('allStyles')}
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
                {t('previous')}
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
                {t('next')}
              </Link>
            </Box>
          )}
        </Flex>
      </Flex>
    );
  };

  const renderContent = () => {
    if (error && !filteredAlbums.length) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>{t('error')}</Heading>
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
          <Heading size="md" mb={6}>{t('albums')}</Heading>
          
          <Flex 
            direction={{ base: 'column', md: 'row' }} 
            gap={4} 
            mb={8} 
            justifyContent="space-between"
            alignItems={{ base: 'stretch', md: 'flex-start' }}
            className="albums-filter"
          >
            <Flex 
              as="ul" 
              className="bottom-ul-menu"
              mb={{ base: 4, md: 0 }}
              flex="1"
              overflowX={{ base: "auto", md: "visible" }}
            >
              {albumFilters.map(filter => (
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
            
            <Select 
              value={sortBy} 
              onChange={(e) => {
                setSortBy(e.target.value);
                setPage(1); // Reset page when changing sort
              }}
              maxW={{ base: '100%', md: '200px' }}
            >
              <option value="name">{t('nameSort')}</option>
              <option value="release_date_newest">{t('newestRelease')}</option>
              <option value="release_date_oldest">{t('oldestRelease')}</option>
              <option value="rating">{t('highestRating')}</option>
            </Select>
          </Flex>
    
          {isLoading || isFilterLoading ? (
            <Flex justify="center" py={10}>
              <Text>{t('loadingAlbums')}</Text>
            </Flex>
          ) : currentPageAlbums.length === 0 ? (
            <Box textAlign="center" py={10}>
              <Text>{t('noAlbumsFound')}</Text>
            </Box>
          ) : (
            <>
              <Flex justify="space-between" mb={4} align="center">
                <Text fontSize="sm" color="gray.600">
                  {t('showingRange', {
                    start: (page - 1) * itemsPerPage + 1,
                    end: Math.min(page * itemsPerPage, filteredAlbums.length),
                    total: filteredAlbums.length,
                    item: t('albumItem'),
                  })}
                </Text>
              </Flex>
              
              <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={3}>
                {currentPageAlbums.map(album => (
                  <AlbumCard key={album.album_id} album={album} />
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

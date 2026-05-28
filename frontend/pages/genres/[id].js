import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, SimpleGrid, Tabs, TabList, Tab, TabPanels, TabPanel, Flex, Link, Divider } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { ArtistCard, AlbumCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';
import { useLanguage } from '../../contexts/LanguageContext';
import { getLocalizedInfo, sanitizeHtmlInfo } from '../../utils/formatters';

export default function GenreDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [genre, setGenre] = useState(null);
  const [relatedArtists, setRelatedArtists] = useState([]);
  const [relatedAlbums, setRelatedAlbums] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const { t, language } = useLanguage();

  useEffect(() => {
    const fetchGenreData = async () => {
      if (!router.isReady || !id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch genre details
        const genreData = await api.getGenre(id);
        setGenre(genreData);
        
        // Fetch related artists
        try {
          const artistsData = await api.getArtistsByGenre(id);
          setRelatedArtists(artistsData);
        } catch (artistErr) {
          console.error('Error fetching artists by genre:', artistErr);
          setRelatedArtists([]);
        }
        
        // Fetch related albums
        try {
          const albumsData = await api.getAlbumsByGenre(id);
          setRelatedAlbums(albumsData);
        } catch (albumErr) {
          console.error('Error fetching albums by genre:', albumErr);
          setRelatedAlbums([]);
        }
        
      } catch (err) {
        console.error('Error fetching genre data:', err);
        setError(t('failedLoadGenreDetails'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchGenreData();
  }, [router.isReady, id]);

  const renderContent = () => {
    if (!router.isReady || !id) {
      return (
        <Box textAlign="center" py={10}>
          <Text>{t('loadingGenreDetails')}</Text>
        </Box>
      );
    }

    if (error) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>{t('error')}</Heading>
          <Text>{error}</Text>
        </Box>
      );
    }

    if (isLoading) {
      return (
        <Box textAlign="center" py={10}>
          <Text>{t('loadingGenreDetails')}</Text>
        </Box>
      );
    }

    if (!genre) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>{t('genreNotFound')}</Heading>
          <Text>{t('genreNotFoundHelp')}</Text>
          <NextLink href="/genres" passHref legacyBehavior>
            <Link color="blue.500" mt={4} display="inline-block">
              {t('backToGenres')}
            </Link>
          </NextLink>
        </Box>
      );
    }

    return (
      <Box>
        <Box mb={8}>
          <Box p={6} borderRadius="lg">
            <Heading size="lg" mb={4} color="gray.800">{genre.name}</Heading>
            <Box
              fontSize="md"
              mb={6}
              sx={{
                'div, p': { mb: 2 },
                strong: { fontWeight: '700' },
              }}
              dangerouslySetInnerHTML={{ __html: sanitizeHtmlInfo(getLocalizedInfo(genre, language)) }}
            />
            
            <Divider my={4} borderColor="gray.200" />
          </Box>
        </Box>
        
        <Box 
          className="detail-tabs"
          mt={8}
        >
          <Flex 
            as="ul" 
            className="bottom-ul-menu"
            mb={4}
          >
            <Box as="li" className={activeTab === 0 ? "active" : ""}>
              <Link onClick={() => setActiveTab(0)}>
                {t('artists')}
              </Link>
            </Box>
            <Box as="li" className={activeTab === 1 ? "active" : ""}>
              <Link onClick={() => setActiveTab(1)}>
                {t('albums')}
              </Link>
            </Box>
          </Flex>
            
          {activeTab === 0 ? (
            <Box>
              {relatedArtists.length === 0 ? (
                <Box py={4}>
                  <Text>{t('noArtistsForGenre')}</Text>
                  <Text fontSize="sm" color="gray.500" mt={2}>
                    {t('genrePlaceholderArtists')}
                  </Text>
                </Box>
              ) : (
                <SimpleGrid columns={{ base: 1, md: 3, lg: 5 }} spacing={3} mt={4}>
                  {relatedArtists.map(artist => (
                    <ArtistCard key={artist.artist_id} artist={artist} />
                  ))}
                </SimpleGrid>
              )}
            </Box>
          ) : (
            <Box>
              {relatedAlbums.length === 0 ? (
                <Box py={4}>
                  <Text>{t('noAlbumsForGenre')}</Text>
                  <Text fontSize="sm" color="gray.500" mt={2}>
                    {t('genrePlaceholderAlbums')}
                  </Text>
                </Box>
              ) : (
                <SimpleGrid columns={{ base: 1, md: 3, lg: 5 }} spacing={3} mt={4}>
                  {relatedAlbums.map(album => (
                    <AlbumCard key={album.album_id} album={album} />
                  ))}
                </SimpleGrid>
              )}
            </Box>
          )}
        </Box>
      </Box>
    );
  };

  return (
    <XiamiuLayout>
      {renderContent()}
    </XiamiuLayout>
  );
} 

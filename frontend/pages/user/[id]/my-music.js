import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import {
  Box,
  Heading,
  Text,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Container,
  Spinner,
  Flex,
  Button,
  Link,
  SimpleGrid,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import XiamiuLayout from '../../../components/Layout/XiamiuLayout';
import { useAuth } from '../../../contexts/AuthContext';
import { api } from '../../../utils/api';
import { useLanguage } from '../../../contexts/LanguageContext';

export default function MyMusic() {
  const router = useRouter();
  const { id } = router.query;
  const { user: currentUser, isAuthenticated, isLoading: authLoading } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState(null);
  const [songComments, setSongComments] = useState([]);
  const [albumComments, setAlbumComments] = useState([]);
  const [artistComments, setArtistComments] = useState([]);
  const [error, setError] = useState(null);
  const { t, language } = useLanguage();

  // Check if the logged-in user is viewing their own My Music page
  const isOwnProfile = currentUser && currentUser.id === parseInt(id);

  useEffect(() => {
    // Don't do anything until authentication is checked
    if (authLoading) return;

    // If not authenticated, redirect to login
    if (!isAuthenticated) {
      router.push('/login?returnUrl=' + encodeURIComponent(router.asPath));
      return;
    }

    // If user is trying to access someone else's My Music page
    if (currentUser && id && parseInt(id) !== currentUser.id) {
      setError(t('cannotAccessOtherMusic'));
      return;
    }

    const fetchUserData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch user details
        const user = await api.getUser(id);
        setUserData(user);

        // Fetch user's comments
        const songs = await api.getUserSongComments(id);
        setSongComments(songs);

        const albums = await api.getUserAlbumComments(id);
        setAlbumComments(albums);

        const artists = await api.getUserArtistComments(id);
        setArtistComments(artists);
      } catch (err) {
        console.error('Error fetching user data:', err);
        setError(t('failedLoadUserDetails'));
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      fetchUserData();
    }
  }, [id, currentUser, isAuthenticated, authLoading, router]);

  if (authLoading || (!userData && isLoading)) {
    return (
      <XiamiuLayout>
        <Container maxW="container.lg" py={10}>
          <Flex justifyContent="center" alignItems="center" minHeight="50vh">
            <Spinner size="xl" color="#f60" />
          </Flex>
        </Container>
      </XiamiuLayout>
    );
  }

  if (error) {
    return (
      <XiamiuLayout>
        <Container maxW="container.lg" py={10}>
          <Alert status="error" borderRadius="md">
            <AlertIcon />
            {error}
          </Alert>
          <Box mt={4} textAlign="center">
            <NextLink href="/" passHref legacyBehavior>
              <Button as="a" colorScheme="orange">
                {t('returnToHome')}
              </Button>
            </NextLink>
          </Box>
        </Container>
      </XiamiuLayout>
    );
  }

  if (!userData) {
    return (
      <XiamiuLayout>
        <Container maxW="container.lg" py={10}>
          <Text>{t('userNotFound')}</Text>
        </Container>
      </XiamiuLayout>
    );
  }

  return (
    <XiamiuLayout>
      <Container maxW="container.lg">
        <Box mb={8}>
          <Heading size="xl" mb={2}>{t('myMusic')}</Heading>
          <Text color="gray.600">{t('welcomeBack', { name: userData.user_name })}</Text>
        </Box>

        <Tabs variant="enclosed" colorScheme="orange">
          <TabList>
            <Tab>{t('albums')}</Tab>
            <Tab>{t('songs')}</Tab>
            <Tab>{t('artists')}</Tab>
          </TabList>

          <TabPanels>
            <TabPanel>
              <Box>
                <Heading size="md" mb={4}>{t('myAlbumComments')}</Heading>
                {albumComments.length > 0 ? (
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    {albumComments.map(comment => (
                      <Box key={comment.id} p={4} borderWidth="1px" borderRadius="md" bg="white">
                        <Flex justifyContent="space-between" mb={2}>
                          <NextLink href={`/albums/${comment.album_id}`} passHref legacyBehavior>
                            <Link fontWeight="bold" color="#f60">
                              {t('albumId', { id: comment.album_id })}
                            </Link>
                          </NextLink>
                          <Text fontSize="sm" color="gray.500">
                            {new Date(comment.review_date).toLocaleDateString(language === 'zh' ? 'zh-CN' : 'en-US')}
                          </Text>
                        </Flex>
                        <Text>{comment.comment}</Text>
                        <Text fontSize="sm" mt={2}>{t('likes', { count: comment.num_like })}</Text>
                      </Box>
                    ))}
                  </SimpleGrid>
                ) : (
                  <Text>{t('noAlbumComments')}</Text>
                )}
              </Box>
            </TabPanel>

            <TabPanel>
              <Box>
                <Heading size="md" mb={4}>{t('mySongComments')}</Heading>
                {songComments.length > 0 ? (
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    {songComments.map(comment => (
                      <Box key={comment.id} p={4} borderWidth="1px" borderRadius="md" bg="white">
                        <Flex justifyContent="space-between" mb={2}>
                          <NextLink href={`/songs/${comment.song_id}`} passHref legacyBehavior>
                            <Link fontWeight="bold" color="#f60">
                              {t('songId', { id: comment.song_id })}
                            </Link>
                          </NextLink>
                          <Text fontSize="sm" color="gray.500">
                            {new Date(comment.review_date).toLocaleDateString(language === 'zh' ? 'zh-CN' : 'en-US')}
                          </Text>
                        </Flex>
                        <Text>{comment.comment}</Text>
                        <Text fontSize="sm" mt={2}>{t('likes', { count: comment.num_like })}</Text>
                      </Box>
                    ))}
                  </SimpleGrid>
                ) : (
                  <Text>{t('noSongComments')}</Text>
                )}
              </Box>
            </TabPanel>

            <TabPanel>
              <Box>
                <Heading size="md" mb={4}>{t('myArtistComments')}</Heading>
                {artistComments.length > 0 ? (
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    {artistComments.map(comment => (
                      <Box key={comment.id} p={4} borderWidth="1px" borderRadius="md" bg="white">
                        <Flex justifyContent="space-between" mb={2}>
                          <NextLink href={`/artists/${comment.artist_id}`} passHref legacyBehavior>
                            <Link fontWeight="bold" color="#f60">
                              {t('artistId', { id: comment.artist_id })}
                            </Link>
                          </NextLink>
                          <Text fontSize="sm" color="gray.500">
                            {new Date(comment.review_date).toLocaleDateString(language === 'zh' ? 'zh-CN' : 'en-US')}
                          </Text>
                        </Flex>
                        <Text>{comment.comment}</Text>
                        <Text fontSize="sm" mt={2}>{t('likes', { count: comment.num_like })}</Text>
                      </Box>
                    ))}
                  </SimpleGrid>
                ) : (
                  <Text>{t('noArtistComments')}</Text>
                )}
              </Box>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Container>
    </XiamiuLayout>
  );
} 

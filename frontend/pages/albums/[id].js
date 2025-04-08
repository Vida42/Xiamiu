import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, Image, Flex, Badge, Link, Divider, Table, Thead, Tbody, Tr, Td, Th, VStack } from '@chakra-ui/react';
import { api } from '../../utils/api';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';

// SectionHeader component for consistent styling
const SectionHeader = ({ title }) => {
  return (
    <Flex justify="space-between" align="center" mb={4}>
      <Heading 
        size="md" 
        fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
        color="black"
        fontWeight="bold"
      >
        {title}
      </Heading>
    </Flex>
  );
};

export default function AlbumDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [album, setAlbum] = useState(null);
  const [albumMeta, setAlbumMeta] = useState(null);
  const [songs, setSongs] = useState([]);
  const [artist, setArtist] = useState(null);
  const [comments, setComments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAlbumData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch album details
        const albumData = await api.getAlbum(id);
        setAlbum(albumData);
        
        // Fetch artist details
        try {
          const artistData = await api.getArtist(albumData.artist_id);
          setArtist(artistData);
        } catch (artistErr) {
          console.log('Failed to load artist details');
        }
        
        // Fetch album's songs
        const songsData = await api.getAlbumSongs(id);
        setSongs(songsData);
        
        // Try to fetch album metadata
        try {
          const metaData = await api.getAlbumMeta(id);
          setAlbumMeta(metaData);
        } catch (metaErr) {
          console.log('No metadata available for this album');
        }
        
        // Try to fetch album comments
        try {
          const commentsData = await api.getAlbumComments(id);
          setComments(commentsData);
        } catch (commentsErr) {
          console.log('No comments available for this album');
        }
        
      } catch (err) {
        console.error('Error fetching album data:', err);
        setError('Failed to load album details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAlbumData();
  }, [id]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const renderContent = () => {
    if (!id) return null;

    if (error) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Error</Heading>
          <Text>{error}</Text>
        </Box>
      );
    }

    if (isLoading) {
      return (
        <Box textAlign="center" py={10}>
          <Text>Loading album details...</Text>
        </Box>
      );
    }

    if (!album) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Album Not Found</Heading>
          <Text>The album you're looking for doesn't exist.</Text>
          <NextLink href="/albums" passHref legacyBehavior>
            <Link color="blue.500" mt={4} display="inline-block">
              Back to Albums
            </Link>
          </NextLink>
        </Box>
      );
    }

    return (
      <Box>
        <Box mb={8}>
          <Flex direction={{ base: 'column', md: 'row' }} gap={8}>
            <Box flexShrink={0} maxW={{ base: '100%', md: '300px' }}>
              <Image
                src={albumMeta?.pic_address || '/album-placeholder.svg'}
                alt={album.name}
                borderRadius="lg"
                width="260px"
                height="260px"
                objectFit="cover"
                crossOrigin="anonymous"
                fallbackSrc="/album-placeholder.svg"
              />
              <Flex justify="center" mt={2}>
                {Array.from({ length: album.star }).map((_, i) => (
                  <Text key={i} fontSize="xl">⭐</Text>
                ))}
              </Flex>
            </Box>
            
            <Box>
              <Heading size="md" mb={4}>{album.name}</Heading>
              
              {artist && (
                <Flex gap={2} mb={4}>
                  <Text width="120px">Artist:</Text>
                  <NextLink href={`/artists/${artist.artist_id}`} passHref legacyBehavior>
                    <Link fontSize="md" color="blue.500">
                      {artist.name}
                    </Link>
                  </NextLink>
                </Flex>
              )}
              
              <Box mt={4}>
                <VStack spacing={2} align="flex-start">
                  <Flex>
                    <Text width="120px">Release Date:</Text>
                    <Text>{formatDate(album.release_date)}</Text>
                  </Flex>
                  
                  <Flex>
                    <Text width="120px">Language:</Text>
                    <Text>{album.album_lan}</Text>
                  </Flex>
                  
                  <Flex>
                    <Text width="120px">Category:</Text>
                    <Text>{album.album_category}</Text>
                  </Flex>
                  
                  {album.record_label && album.record_label !== "''" && (
                    <Flex>
                      <Text fontWeight="bold" width="120px">Record Label:</Text>
                      <Text>{album.record_label}</Text>
                    </Flex>
                  )}
                </VStack>
              </Box>
              
              {albumMeta && albumMeta.info && (
                <Box mt={6} mb={4}>
                  <Heading as="h3" size="md" mb={3}>Description</Heading>
                  <Text fontSize="md" lineHeight="1.7" px={3} py={4} bg="gray.50" borderRadius="md">
                    {albumMeta.info}
                  </Text>
                </Box>
              )}
              
              <Divider my={4} />
            </Box>
          </Flex>
        </Box>
        
        {/* Songs Section */}
        <Box mt={8} mb={8}>
          <SectionHeader title={`Songs (${songs.length})`} />
          
          {songs.length === 0 ? (
            <Text py={4}>No songs available for this album.</Text>
          ) : (
            <Box mt={4}>
              <Table variant="simple" size="md">
                <Thead>
                  <Tr borderBottom="1px solid" borderColor="gray.200">
                    <Th width="60px" textAlign="center" fontWeight="normal" fontSize="sm" color="gray.500" py={3}>#</Th>
                    <Th fontWeight="normal" fontSize="sm" color="gray.500" py={3}>Song</Th>
                    <Th width="120px" fontWeight="normal" fontSize="sm" color="gray.500" py={3}>Rating</Th>
                    <Th fontWeight="normal" fontSize="sm" color="gray.500" py={3}>Artist</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {songs.map((song, index) => (
                    <Tr key={song.song_id} borderBottom="1px solid" borderColor="gray.100">
                      <Td textAlign="center" color="gray.500" fontSize="sm" py={3}>{index + 1}</Td>
                      <Td py={3}>
                        <NextLink href={`/songs/${song.song_id}`} passHref legacyBehavior>
                          <Link 
                            color="black" 
                            _hover={{ textDecoration: 'underline' }}
                            fontSize="sm"
                          >
                            {song.name}
                          </Link>
                        </NextLink>
                      </Td>
                      <Td py={3}>
                        {Array.from({ length: song.star }).map((_, i) => (
                          <Text as="span" key={i} fontSize="xs">⭐</Text>
                        ))}
                      </Td>
                      <Td py={3}>
                        {artist && (
                          <NextLink href={`/artists/${artist.artist_id}`} passHref legacyBehavior>
                            <Link 
                              color="gray.600" 
                              fontSize="sm"
                              _hover={{ textDecoration: 'underline' }}
                            >
                              {artist.name}
                            </Link>
                          </NextLink>
                        )}
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </Box>
          )}
        </Box>
        
        {/* Comments Section */}
        <Box mt={8} mb={8}>
          <SectionHeader title={`Comments (${comments.length})`} />
          
          {comments.length === 0 ? (
            <Text py={4}>No comments available for this album.</Text>
          ) : (
            <Box mt={4}>
              {comments.map(comment => (
                <Box 
                  key={comment.id} 
                  p={4} 
                  borderWidth="1px" 
                  borderRadius="md"
                  mb={4}
                >
                  <Text>{comment.comment}</Text>
                  <Flex mt={2} justify="space-between" alignItems="center">
                    <Text fontSize="sm" color="gray.500">
                      Posted on {new Date(comment.review_date).toLocaleDateString()}
                    </Text>
                    <Badge colorScheme="green">
                      {comment.num_like} likes
                    </Badge>
                  </Flex>
                </Box>
              ))}
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
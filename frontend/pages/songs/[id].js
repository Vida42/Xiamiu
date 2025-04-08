import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, Image, Flex, Badge, Link, Divider, VStack } from '@chakra-ui/react';
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

export default function SongDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [song, setSong] = useState(null);
  const [songMeta, setSongMeta] = useState(null);
  const [album, setAlbum] = useState(null);
  const [albumMeta, setAlbumMeta] = useState(null);
  const [artist, setArtist] = useState(null);
  const [comments, setComments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSongData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch song details
        const songData = await api.getSong(id);
        setSong(songData);
        
        // Fetch album details
        if (songData.album_id) {
          try {
            const albumData = await api.getAlbum(songData.album_id);
            setAlbum(albumData);
            
            // Fetch album metadata to get cover image
            try {
              const albumMetaData = await api.getAlbumMeta(songData.album_id);
              setAlbumMeta(albumMetaData);
            } catch (albumMetaErr) {
              console.log('No album metadata available');
            }
            
            // Fetch artist details
            if (albumData.artist_id) {
              try {
                const artistData = await api.getArtist(albumData.artist_id);
                setArtist(artistData);
              } catch (artistErr) {
                console.log('Failed to load artist details');
              }
            }
          } catch (albumErr) {
            console.log('Failed to load album details');
          }
        }
        
        // Try to fetch song metadata (lyrics)
        try {
          const metaData = await api.getSongMeta(id);
          setSongMeta(metaData);
        } catch (metaErr) {
          console.log('No metadata available for this song');
        }
        
        // Try to fetch song comments
        try {
          const commentsData = await api.getSongComments(id);
          setComments(commentsData);
        } catch (commentsErr) {
          console.log('No comments available for this song');
        }
        
      } catch (err) {
        console.error('Error fetching song data:', err);
        setError('Failed to load song details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSongData();
  }, [id]);

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
          <Text>Loading song details...</Text>
        </Box>
      );
    }

    if (!song) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Song Not Found</Heading>
          <Text>The song you're looking for doesn't exist.</Text>
          <NextLink href="/songs" passHref legacyBehavior>
            <Link color="blue.500" mt={4} display="inline-block">
              Back to Songs
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
                alt={album?.name || song.name}
                borderRadius="lg"
                width="260px"
                height="260px"
                objectFit="cover"
                crossOrigin="anonymous"
                fallbackSrc="/album-placeholder.svg"
              />
              <Flex justify="center" mt={2}>
                {Array.from({ length: song.star }).map((_, i) => (
                  <Text key={i} fontSize="xl">⭐</Text>
                ))}
              </Flex>
            </Box>
            
            <Box>
              <Heading size="lg" mb={4}>{song.name}</Heading>
              
              <Box mt={4}>
                <VStack spacing={3} align="flex-start">
                  <Flex>
                    <Text width="120px" fontWeight="medium">Artist:</Text>
                    {artist ? (
                      <NextLink href={`/artists/${artist.artist_id}`} passHref legacyBehavior>
                        <Link fontSize="md" color="blue.500" _hover={{ textDecoration: 'underline' }}>
                          {artist.name}
                        </Link>
                      </NextLink>
                    ) : (
                      <Text fontSize="md" color="gray.600">Unknown Artist</Text>
                    )}
                  </Flex>
                  
                  {album && (
                    <Flex>
                      <Text width="120px" fontWeight="medium">Album:</Text>
                      <NextLink href={`/albums/${album.album_id}`} passHref legacyBehavior>
                        <Link color="blue.500" fontSize="md" _hover={{ textDecoration: 'underline' }}>
                          {album.name}
                        </Link>
                      </NextLink>
                    </Flex>
                  )}
                  
                  <Flex>
                    <Text width="120px" fontWeight="medium">Rating:</Text>
                    <Text>{song.star} / 5</Text>
                  </Flex>
                </VStack>
              </Box>
              
              <Divider my={4} />
            </Box>
          </Flex>
        </Box>
        
        {/* Lyrics Section */}
        <Box mt={8} mb={8}>
          <SectionHeader title="Lyrics" />
          
          {songMeta ? (
            <Box 
              whiteSpace="pre-wrap" 
              p={6} 
              bg="gray.50" 
              borderRadius="md"
              fontFamily="body"
              lineHeight="tall"
            >
              {songMeta.lyrics}
            </Box>
          ) : (
            <Text py={4}>No lyrics available for this song.</Text>
          )}
        </Box>
        
        {/* Comments Section */}
        <Box mt={8} mb={8}>
          <SectionHeader title={`Comments (${comments.length})`} />
          
          {comments.length === 0 ? (
            <Text py={4}>No comments available for this song.</Text>
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
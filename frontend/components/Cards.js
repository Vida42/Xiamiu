import { Box, Image, Heading, Text, Badge, Stack, LinkBox, LinkOverlay, Flex } from '@chakra-ui/react';
import { useState, useEffect } from 'react';
import NextLink from 'next/link';
import { api } from '../utils/api';

export const ArtistCard = ({ artist }) => {
  const [artistMeta, setArtistMeta] = useState(null);
  
  useEffect(() => {
    const fetchArtistMeta = async () => {
      try {
        const meta = await api.getArtistMeta(artist.artist_id);
        setArtistMeta(meta);
      } catch (error) {
        console.error(`Error fetching artist metadata for ${artist.artist_id}:`, error);
      }
    };
    
    fetchArtistMeta();
  }, [artist.artist_id]);

  return (
    <LinkBox as="article">
      <Box
        maxW="sm"
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        transition="transform 0.3s"
        _hover={{ transform: 'scale(1.03)' }}
      >
        <Image
          src={artistMeta?.pic_address || `/placeholder-artist.jpg`}
          alt={artist.name}
          height="200px"
          width="100%"
          objectFit="cover"
          crossOrigin="anonymous"
          fallbackSrc="/placeholder-artist.jpg"
        />
        <Box p={4}>
          <NextLink href={`/artists/${artist.artist_id}`} passHref legacyBehavior>
            <LinkOverlay>
              <Heading size="md" mb={2}>{artist.name}</Heading>
            </LinkOverlay>
          </NextLink>
          <Text color="gray.500" fontSize="sm">
            Reign: {artist.reign}
          </Text>
        </Box>
      </Box>
    </LinkBox>
  );
};

export const AlbumCard = ({ album }) => {
  const [albumMeta, setAlbumMeta] = useState(null);
  
  useEffect(() => {
    const fetchAlbumMeta = async () => {
      try {
        const meta = await api.getAlbumMeta(album.album_id);
        setAlbumMeta(meta);
      } catch (error) {
        console.error(`Error fetching album metadata for ${album.album_id}:`, error);
      }
    };
    
    fetchAlbumMeta();
  }, [album.album_id]);
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <LinkBox as="article">
      <Box
        maxW="sm"
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        transition="transform 0.3s"
        _hover={{ transform: 'scale(1.03)' }}
      >
        <Image
          src={albumMeta?.pic_address || `/placeholder-album.jpg`}
          alt={album.name}
          height="200px"
          width="100%"
          objectFit="cover"
          crossOrigin="anonymous"
          fallbackSrc="/placeholder-album.jpg"
        />
        <Box p={4}>
          <NextLink href={`/albums/${album.album_id}`} passHref legacyBehavior>
            <LinkOverlay>
              <Heading size="md" mb={2}>{album.name}</Heading>
            </LinkOverlay>
          </NextLink>
          <Flex justifyContent="space-between" alignItems="center">
            <Text color="gray.500" fontSize="sm">
              Released: {formatDate(album.release_date)}
            </Text>
            <Stack direction="row">
              {Array.from({ length: album.star }).map((_, i) => (
                <span key={i}>⭐</span>
              ))}
            </Stack>
          </Flex>
        </Box>
      </Box>
    </LinkBox>
  );
};

export const SongCard = ({ song }) => {
  return (
    <LinkBox as="article">
      <Box
        p={4}
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        transition="transform 0.3s"
        _hover={{ transform: 'scale(1.03)', bg: 'gray.50' }}
      >
        <NextLink href={`/songs/${song.song_id}`} passHref legacyBehavior>
          <LinkOverlay>
            <Heading size="sm" mb={2}>{song.name}</Heading>
          </LinkOverlay>
        </NextLink>
        <Flex justifyContent="space-between" alignItems="center">
          <Text fontSize="xs" color="gray.500">Album: {song.album_id}</Text>
          <Badge colorScheme="yellow">
            {Array.from({ length: song.star }).map((_, i) => (
              <span key={i}>⭐</span>
            ))}
          </Badge>
        </Flex>
      </Box>
    </LinkBox>
  );
};

export const GenreCard = ({ genre }) => {
  return (
    <LinkBox as="article">
      <Box
        p={4}
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        bg="purple.50"
        transition="transform 0.3s"
        _hover={{ transform: 'scale(1.03)', bg: 'purple.100' }}
      >
        <NextLink href={`/genres/${genre.id}`} passHref legacyBehavior>
          <LinkOverlay>
            <Heading size="sm" mb={2}>{genre.name}</Heading>
          </LinkOverlay>
        </NextLink>
        <Text fontSize="xs" noOfLines={2}>{genre.info}</Text>
      </Box>
    </LinkBox>
  );
}; 
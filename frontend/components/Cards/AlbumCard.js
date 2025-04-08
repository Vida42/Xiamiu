import { Box, Image, Text, LinkBox, LinkOverlay, Heading, Flex, Stack } from '@chakra-ui/react';
import NextLink from 'next/link';
import { useState, useEffect } from 'react';
import { api } from '../../utils/api';

const AlbumCard = ({ album }) => {
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
        w="100%"
        h="100%"
        borderWidth="1px"
        borderRadius="md"
        overflow="hidden"
        transition="transform 0.3s"
        _hover={{ transform: 'scale(1.03)' }}
      >
        <Image
          src={albumMeta?.pic_address || `/placeholder-album.jpg`}
          alt={album.name}
          height="140px"
          width="100%"
          objectFit="cover"
          crossOrigin="anonymous"
          fallbackSrc="/placeholder-album.jpg"
        />
        <Box pt={1} px={2} pb={1}>
          <NextLink href={`/albums/${album.album_id}`} passHref legacyBehavior>
            <LinkOverlay>
              <Text size="sm" mb={0.5}>{album.name}</Text>
            </LinkOverlay>
          </NextLink>
          <Flex justifyContent="space-between" alignItems="center">
            <Text color="gray.500" fontSize="xs">
              {formatDate(album.release_date)}
            </Text>
            <Stack direction="row" spacing={0.5}>
              {Array.from({ length: album.star }).map((_, i) => (
                <Text key={i} fontSize="10px" lineHeight="1">⭐</Text>
              ))}
            </Stack>
          </Flex>
        </Box>
      </Box>
    </LinkBox>
  );
};
export default AlbumCard; 
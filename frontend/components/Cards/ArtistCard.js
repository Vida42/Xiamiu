import {useEffect, useState} from "react";
import {api} from "../../utils/api";
import {Box, Heading, Image, LinkBox, LinkOverlay, Text} from "@chakra-ui/react";
import NextLink from "next/link";

const ArtistCard = ({ artist }) => {
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
        w="100%"
        h="100%"
        borderWidth="1px"
        borderRadius="md"
        overflow="hidden"
        transition="transform 0.3s"
        _hover={{ transform: 'scale(1.03)' }}
      >
        <Image
          src={artistMeta?.pic_address || `/placeholder-artist.jpg`}
          alt={artist.name}
          height="140px"
          width="100%"
          objectFit="cover"
          crossOrigin="anonymous"
          fallbackSrc="/placeholder-artist.jpg"
        />
        <Box pt={1} px={2} pb={1}>
          <NextLink href={`/artists/${artist.artist_id}`} passHref legacyBehavior>
            <LinkOverlay>
              <Heading size="sm" mb={0.5}>{artist.name}</Heading>
            </LinkOverlay>
          </NextLink>
          <Text color="gray.500" fontSize="xs">
            {artist.region}
          </Text>
        </Box>
      </Box>
    </LinkBox>
  );
};

export default ArtistCard;

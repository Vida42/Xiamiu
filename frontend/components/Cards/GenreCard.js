import {Box, Heading, LinkBox, LinkOverlay, Text} from "@chakra-ui/react";
import NextLink from "next/link";
import AlbumCard from "./AlbumCard";

const GenreCard = ({ genre }) => {
  return (
    <LinkBox as="article">
      <Box
        p={2}
        borderWidth="1px"
        borderRadius="md"
        overflow="hidden"
        transition="transform 0.3s"
        _hover={{ transform: 'scale(1.03)', bg: 'gray.50' }}
      >
        <NextLink href={`/genres/${genre.id}`} passHref legacyBehavior>
          <LinkOverlay>
            <Heading size="sm" mb={1}>{genre.name}</Heading>
          </LinkOverlay>
        </NextLink>
        <Text fontSize="xs" noOfLines={2}>{genre.info}</Text>
      </Box>
    </LinkBox>
  );
};

export default GenreCard;

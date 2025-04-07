import { Box, Container, Flex, Link, Heading, Input, InputGroup, InputRightElement, IconButton } from '@chakra-ui/react';
import NextLink from 'next/link';
import { useRouter } from 'next/router';
import { useState } from 'react';

const NavLink = ({ href, children }) => {
  const router = useRouter();
  const isActive = router.pathname === href || router.asPath.startsWith(href);

  return (
    <NextLink href={href} passHref legacyBehavior>
      <Link
        px={4}
        py={2}
        rounded={'md'}
        fontWeight={isActive ? 'bold' : 'normal'}
        color={isActive ? 'blue.500' : 'gray.700'}
        _hover={{
          textDecoration: 'none',
          color: 'blue.500',
        }}
      >
        {children}
      </Link>
    </NextLink>
  );
};

export default function Layout({ children }) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?query=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <Box minH="100vh">
      <Box bg="white" borderBottom="1px" borderColor="gray.200" position="fixed" width="100%" zIndex={10}>
        <Container maxW="container.xl">
          <Flex as="nav" py={4} justifyContent="space-between" alignItems="center">
            <Flex alignItems="center">
              <NextLink href="/" passHref legacyBehavior>
                <Link _hover={{ textDecoration: 'none' }}>
                  <Heading size="md" color="blue.600">Xiamiu Music</Heading>
                </Link>
              </NextLink>
              <Flex ml={10}>
                <NavLink href="/artists">Artists</NavLink>
                <NavLink href="/albums">Albums</NavLink>
                <NavLink href="/songs">Songs</NavLink>
                <NavLink href="/genres">Genres</NavLink>
              </Flex>
            </Flex>
            <form onSubmit={handleSearch}>
              <InputGroup size="md" width="300px">
                <Input
                  pr="4.5rem"
                  placeholder="Search artists, albums, songs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <InputRightElement width="4.5rem">
                  <IconButton
                    h="1.75rem"
                    size="sm"
                    type="submit"
                    aria-label="Search"
                    icon={<span>🔍</span>}
                  />
                </InputRightElement>
              </InputGroup>
            </form>
          </Flex>
        </Container>
      </Box>
      <Box as="main" pt="72px" pb={8}>
        <Container maxW="container.xl">
          {children}
        </Container>
      </Box>
      <Box as="footer" py={4} borderTop="1px" borderColor="gray.200">
        <Container maxW="container.xl" textAlign="center" color="gray.500">
          © {new Date().getFullYear()} Xiamiu Music. All rights reserved.
        </Container>
      </Box>
    </Box>
  );
} 
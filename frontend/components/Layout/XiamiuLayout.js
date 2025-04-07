import { Box, Flex, Container, Link, Input, InputGroup, InputLeftElement, useColorModeValue, Text } from '@chakra-ui/react';
import NextLink from 'next/link';
import { SearchIcon } from '@chakra-ui/icons';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { useState } from 'react';

const NavLink = ({ href, children, isActive }) => {
  return (
    <Box
      as={NextLink}
      href={href}
      px={4}
      py={2}
      _hover={{
        textDecoration: 'none',
        bg: 'rgba(255, 255, 255, 0.1)',
      }}
      color="white"
      display="block"
      fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
      fontWeight={isActive ? 'bold' : 'normal'}
    >
      {children}
    </Box>
  );
};

const SubNavLink = ({ href, children, isActive }) => {
  return (
    <Box
      as={NextLink}
      href={href}
      className={isActive ? "active" : ""}
      display="inline-block"
      height="100%"
      px="20px"
      lineHeight="35px"
      fontSize="14px"
      textDecoration="none"
      _hover={{
        backgroundColor: "#e6e6e6",
        color: "#f60"
      }}
      backgroundColor={isActive ? "#e6e6e6" : "transparent"}
      color={isActive ? "#f60" : "#333"}
      fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
    >
      {children}
    </Box>
  );
};

const XiamiuLayout = ({ children }) => {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');

  // Handle search functionality
  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      const query = e.target.value.trim();
      if (query) {
        router.push(`/search?q=${encodeURIComponent(query)}`);
      }
    }
  };

  return (
    <Box fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif">
      <Head>
        <title>Xiamiu Music</title>
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
          
          body {
            font-family: 'Microsoft YaHei', 'STHeiti', 'Noto Sans SC', sans-serif;
          }
        `}</style>
      </Head>
      
      {/* Main Orange Navigation Bar (header-top) */}
      <Box className="header-top">
        <Container maxW="container.xl">
          <Flex h="60px" alignItems="center" justifyContent="space-between">
            {/* Logo and Main Nav */}
            <Flex alignItems="center" gap={4}>
              <Box
                as={NextLink}
                href="/"
                fontSize="24px"
                fontWeight="bold"
                _hover={{ textDecoration: 'none' }}
                letterSpacing="tight"
                color="white"
              >
                Xiamiu
              </Box>
              <NavLink href="/" isActive={router.pathname === '/'}>
                发现音乐
              </NavLink>
              <NavLink href="/my-music" isActive={router.pathname === '/my-music'}>
                我的音乐
              </NavLink>
            </Flex>

            {/* Search Bar */}
            <InputGroup maxW="300px">
              <InputLeftElement pointerEvents="none">
                <SearchIcon color="gray.300" />
              </InputLeftElement>
              <Input
                placeholder="音乐搜索..."
                bg="white"
                color="gray.800"
                _placeholder={{ color: 'gray.400' }}
                onKeyDown={handleSearch}
                onChange={(e) => setSearchQuery(e.target.value)}
                value={searchQuery}
                borderRadius="full"
                size="sm"
              />
            </InputGroup>

            {/* Auth Links */}
            <Flex gap={4}>
              <Box
                as="button"
                color="white"
                _hover={{ textDecoration: 'underline' }}
                fontSize="14px"
                fontWeight="medium"
              >
                登录
              </Box>
              <Box
                as="button"
                color="white"
                _hover={{ textDecoration: 'underline' }}
                fontSize="14px"
                fontWeight="medium"
              >
                注册
              </Box>
            </Flex>
          </Flex>
        </Container>
      </Box>

      {/* Sub Navigation (header-bottom) */}
      <Box className="header-bottom">
        <Container maxW="container.xl">
          <Flex as="ul" className="nav">
            <Box as="li">
              <SubNavLink href="/" isActive={router.pathname === '/'}>
                热门
              </SubNavLink>
            </Box>
            <Box as="li">
              <SubNavLink href="/albums" isActive={router.pathname.startsWith('/albums')}>
                专辑
              </SubNavLink>
            </Box>
            <Box as="li">
              <SubNavLink href="/artists" isActive={router.pathname.startsWith('/artists')}>
                艺人
              </SubNavLink>
            </Box>
            <Box as="li">
              <SubNavLink href="/genres" isActive={router.pathname.startsWith('/genres')}>
                风格
              </SubNavLink>
            </Box>
          </Flex>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxW="container.xl" py={6}>
        {children}
      </Container>

      {/* Footer */}
      <Box bg="white" py={8} borderTop="1px" borderColor="gray.200">
        <Container maxW="container.xl">
          <Flex justifyContent="center" mb={4}>
            <Box
              as={NextLink} 
              href="/"
              color="gray.500"
              fontSize="sm"
              _hover={{ color: '#f60' }}
            >
              © {new Date().getFullYear()} Xiamiu Music
            </Box>
          </Flex>
        </Container>
      </Box>
    </Box>
  );
};

export default XiamiuLayout;
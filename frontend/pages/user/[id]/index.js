import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import {
  Box,
  Heading,
  Text,
  VStack,
  Flex,
  Link,
  Badge,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Avatar,
  SimpleGrid,
  Container,
  Divider
} from '@chakra-ui/react';
import { api } from '../../../utils/api';
import XiamiuLayout from '../../../components/Layout/XiamiuLayout';
import { useAuth } from '../../../contexts/AuthContext';

export default function UserProfile() {
  const router = useRouter();
  const { id } = router.query;
  const [userData, setUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user: currentUser } = useAuth();
  
  // Check if the logged-in user is viewing their own profile
  const isOwnProfile = currentUser && currentUser.id === parseInt(id);

  useEffect(() => {
    const fetchUserData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch user details
        const user = await api.getUser(id);
        setUserData(user);
      } catch (err) {
        console.error('Error fetching user data:', err);
        setError('Failed to load user details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, [id]);

  if (!id) return null;

  if (error) {
    return (
      <XiamiuLayout>
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Error</Heading>
          <Text>{error}</Text>
        </Box>
      </XiamiuLayout>
    );
  }

  if (isLoading) {
    return (
      <XiamiuLayout>
        <Box textAlign="center" py={10}>
          <Text>Loading user profile...</Text>
        </Box>
      </XiamiuLayout>
    );
  }

  if (!userData) {
    return (
      <XiamiuLayout>
        <Box textAlign="center" py={10}>
          <Heading mb={4}>User Not Found</Heading>
          <Text>The user you're looking for doesn't exist.</Text>
          <NextLink href="/" passHref legacyBehavior>
            <Link color="blue.500" mt={4} display="inline-block">
              Back to Home
            </Link>
          </NextLink>
        </Box>
      </XiamiuLayout>
    );
  }

  return (
    <XiamiuLayout>
      <Container maxW="container.lg">
        <Flex 
          direction={{ base: 'column', md: 'row' }} 
          gap={8} 
          mb={8}
        >
          {/* Profile Sidebar */}
          <Box 
            width={{ base: '100%', md: '300px' }} 
            flexShrink={0}
          >
            <VStack 
              spacing={6} 
              align="center" 
              p={6}
              borderWidth="1px"
              borderRadius="lg"
              bg="white"
            >
              <Avatar 
                size="2xl" 
                name={userData.user_name} 
                bg="orange.500" 
              />
              
              <VStack spacing={2} align="center">
                <Heading size="lg">{userData.user_name}</Heading>
                <Text color="gray.600">Joined: {new Date(userData.join_time).toLocaleDateString()}</Text>
              </VStack>
              
              <SimpleGrid columns={2} spacing={4} width="100%">
                <Box textAlign="center">
                  <Text color="gray.600">Location</Text>
                  <Text fontWeight="bold">{userData.location}</Text>
                </Box>
                <Box textAlign="center">
                  <Text color="gray.600">Age</Text>
                  <Text fontWeight="bold">{userData.age}</Text>
                </Box>
                <Box textAlign="center">
                  <Text color="gray.600">Gender</Text>
                  <Text fontWeight="bold">{userData.gender}</Text>
                </Box>
                <Box textAlign="center">
                  <Text color="gray.600">Plays</Text>
                  <Text fontWeight="bold">{userData.play_count}</Text>
                </Box>
              </SimpleGrid>
              
              {isOwnProfile && (
                <Box width="100%" mt={4}>
                  <NextLink href={`/user/${id}/my-music`} passHref legacyBehavior>
                    <Link
                      display="block"
                      bg="#f60"
                      color="white"
                      py={2}
                      px={4}
                      borderRadius="md"
                      textAlign="center"
                      _hover={{ bg: 'orange.600' }}
                    >
                      My Music
                    </Link>
                  </NextLink>
                </Box>
              )}
            </VStack>
          </Box>
          
          {/* Main Content */}
          <Box flex="1">
            <Tabs variant="enclosed" colorScheme="orange">
              <TabList>
                <Tab>Overview</Tab>
              </TabList>
              
              <TabPanels>
                <TabPanel p={4}>
                  <VStack spacing={6} align="stretch">
                    <Box>
                      <Heading size="md" mb={4}>About</Heading>
                      <Text>
                        This is {userData.user_name}'s profile on Xiamiu. Here you can view their music preferences and comments.
                      </Text>
                    </Box>
                    
                    <Divider />
                    
                    <Box>
                      <Heading size="md" mb={4}>Music Activity</Heading>
                      <Flex justify="space-between" mb={4}>
                        <NextLink href={`/user/${id}/my-music`} passHref legacyBehavior>
                          <Link color="#f60">
                            View all music activity →
                          </Link>
                        </NextLink>
                      </Flex>
                    </Box>
                  </VStack>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Box>
        </Flex>
      </Container>
    </XiamiuLayout>
  );
} 
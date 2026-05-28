import { ChakraProvider } from '@chakra-ui/react';
import theme from '../styles/theme';
import '../styles/globals.css';
import { AuthProvider } from '../contexts/AuthContext';
import { LanguageProvider } from '../contexts/LanguageContext';

function MyApp({ Component, pageProps }) {
  return (
    <ChakraProvider theme={theme}>
      <LanguageProvider>
        <AuthProvider>
          <Component {...pageProps} />
        </AuthProvider>
      </LanguageProvider>
    </ChakraProvider>
  );
}

export default MyApp; 

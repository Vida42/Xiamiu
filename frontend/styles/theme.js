import { extendTheme } from '@chakra-ui/react';

const fonts = {
  body: "'Microsoft YaHei', 'STHeiti', 'Noto Sans SC', sans-serif",
  heading: "'Microsoft YaHei', 'STHeiti', 'Noto Sans SC', sans-serif",
  mono: "Menlo, monospace",
};

const colors = {
  orange: {
    50: '#fff3e0',
    100: '#ffe0b2',
    200: '#ffcc80',
    300: '#ffb74d',
    400: '#ffa726',
    500: '#f60', // Original orange from the header-bg.jpg
    600: '#e65c00',
    700: '#d65600',
    800: '#c64900',
    900: '#b64000',
  },
  xiamiOrange: '#f60', // Exact orange color
};

const components = {
  Link: {
    baseStyle: {
      _hover: {
        textDecoration: 'none',
      },
    },
  },
  Button: {
    variants: {
      solid: {
        bg: 'xiamiOrange',
        color: 'white',
        _hover: {
          bg: 'orange.700',
        },
      },
    },
  },
  Heading: {
    baseStyle: {
      fontFamily: "'Microsoft YaHei', 'STHeiti', 'Noto Sans SC', sans-serif",
      fontWeight: 'bold',
    },
  },
  Text: {
    baseStyle: {
      fontFamily: "'Microsoft YaHei', 'STHeiti', 'Noto Sans SC', sans-serif",
    },
  },
};

const config = {
  initialColorMode: 'light',
  useSystemColorMode: false,
};

const theme = extendTheme({
  fonts,
  colors,
  components,
  config,
});

export default theme; 
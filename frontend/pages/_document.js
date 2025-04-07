import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="zh-CN">
      <Head>
        {/* Add Chinese fonts for Xiami style */}
        <link 
          rel="stylesheet" 
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" 
        />
        <style jsx global>{`
          @font-face {
            font-family: 'Microsoft YaHei';
            src: local('Microsoft YaHei');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
          }
          
          @font-face {
            font-family: 'STHeiti';
            src: local('STHeiti');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
          }
        `}</style>
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
} 
import type { AppProps } from 'next/app';
import { DocsBackground } from '../components/DocsBackground';
import './styles.css';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <DocsBackground />
      <Component {...pageProps} />
    </>
  );
}

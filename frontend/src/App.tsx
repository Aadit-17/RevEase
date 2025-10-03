import { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { InboxPage } from './components/InboxPage';
import { DetailPage } from './components/DetailPage';
import { AnalyticsPage } from './components/AnalyticsPage';
import { Toaster } from './components/ui/sonner';
import { Review } from './data/mockData';
import { ensureSessionId } from './services/api';

export default function App() {
  // Ensure dark mode is applied
  useEffect(() => {
    document.documentElement.classList.add('dark');
    // Ensure session ID exists
    ensureSessionId();
  }, []);

  const [currentPage, setCurrentPage] = useState<string>('inbox');
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);

  const handleNavigate = (page: string) => {
    setCurrentPage(page);
    setSelectedReview(null);
  };

  const handleSelectReview = (review: Review) => {
    setSelectedReview(review);
    setCurrentPage('detail');
  };

  const handleBackToInbox = () => {
    setSelectedReview(null);
    setCurrentPage('inbox');
  };

  const handleReviewUpdate = (updatedReview: Review) => {
    setSelectedReview(updatedReview);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'inbox':
        return <InboxPage onSelectReview={handleSelectReview} />;
      case 'detail':
        return selectedReview ? (
          <DetailPage review={selectedReview} onBack={handleBackToInbox} onReviewUpdate={handleReviewUpdate} />
        ) : (
          <InboxPage onSelectReview={handleSelectReview} />
        );
      case 'analytics':
        return <AnalyticsPage />;
      default:
        return <InboxPage onSelectReview={handleSelectReview} />;
    }
  };

  return (
    <div className="size-full">
      <Layout currentPage={currentPage} onNavigate={handleNavigate}>
        {renderPage()}
      </Layout>
      <Toaster />
    </div>
  );
}
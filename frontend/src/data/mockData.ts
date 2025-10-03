export interface Review {
  id: number;  // Changed from string to number to match backend
  session_id: string;
  location: string;
  rating: number;
  text: string;
  date: string;       // ISO timestamp
  sentiment?: string;
  topic?: string;
  reply?: string;     // AI-generated reply
  created_at: string;
}

export interface ReviewCreate {
  session_id: string;
  location: string;
  rating: number;
  text: string;
  date: string; // ISO timestamp
  topic?: string; // Make topic optional as it can be provided by user
}

// Sample reviews data - only includes fields that a user would provide
export const sampleReviews: Omit<ReviewCreate, 'session_id'>[] = [
  {
    location: "Downtown Branch",
    rating: 5,
    text: "Exceptional service and staff were incredibly helpful. The facility was spotless and the atmosphere was very welcoming. I would definitely recommend this location to others.",
    date: new Date().toISOString(),
    topic: "service"
  },
  {
    location: "Mall Location",
    rating: 2,
    text: "Very disappointed with the cleanliness of the establishment. Tables were dirty and the floor had not been mopped. Staff seemed overwhelmed and service was slow.",
    date: new Date(Date.now() - 86400000).toISOString(), // Yesterday
    topic: "cleanliness"
  },
  {
    location: "Airport Terminal",
    rating: 4,
    text: "Good overall experience. Prices are reasonable and the location is convenient. Service could be faster during peak hours but staff was friendly.",
    date: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
    topic: "price"
  },
  {
    location: "Westside Plaza",
    rating: 3,
    text: "Average experience. Nothing particularly good or bad to report. The service was adequate and the facility was acceptable.",
    date: new Date(Date.now() - 259200000).toISOString(), // 3 days ago
    topic: "service"
  },
  {
    location: "Downtown Branch",
    rating: 1,
    text: "Terrible experience. Overpriced for what you get and the staff was rude. Would not return and will tell others to avoid this location.",
    date: new Date(Date.now() - 345600000).toISOString(), // 4 days ago
    topic: "price"
  },
  {
    location: "Mall Location",
    rating: 5,
    text: "Outstanding service! The staff went above and beyond to help us. Everything was clean and well-organized. Highly recommend!",
    date: new Date(Date.now() - 432000000).toISOString(), // 5 days ago
    topic: "service"
  },
  {
    location: "Airport Terminal",
    rating: 4,
    text: "Clean facilities and decent service. Prices are a bit high but expected for an airport location. Staff was professional.",
    date: new Date(Date.now() - 518400000).toISOString(), // 6 days ago
    topic: "cleanliness"
  },
  {
    location: "Westside Plaza",
    rating: 3,
    text: "It was okay. The food was decent but nothing special. The location is convenient for travelers but quite expensive.",
    date: new Date(Date.now() - 604800000).toISOString(), // 7 days ago
    topic: "price"
  },
  {
    location: "Downtown Branch",
    rating: 2,
    text: "Poor customer service. Waited over 30 minutes just to be seated. The staff seemed disinterested in helping customers. Very disappointed.",
    date: new Date(Date.now() - 691200000).toISOString(), // 8 days ago
    topic: "service"
  },
  {
    location: "Mall Location",
    rating: 5,
    text: "Absolutely fantastic! The new interior design is beautiful and the staff is incredibly friendly. Will definitely be coming back with my family.",
    date: new Date(Date.now() - 777600000).toISOString(), // 9 days ago
    topic: "cleanliness"
  },
  {
    location: "Airport Terminal",
    rating: 4,
    text: "Very satisfied with my visit. The staff was attentive and the environment was clean and comfortable. Will recommend to friends.",
    date: new Date(Date.now() - 864000000).toISOString(), // 10 days ago
    topic: "service"
  },
  {
    location: "Westside Plaza",
    rating: 3,
    text: "Good service overall. Staff was helpful and the place was clean. Could improve on wait times during lunch rush.",
    date: new Date(Date.now() - 950400000).toISOString(), // 11 days ago
    topic: "service"
  }
];
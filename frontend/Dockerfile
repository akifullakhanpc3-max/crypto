# Use Node 18 Alpine
FROM node:18-alpine

# Set working directory to your frontend
WORKDIR /app/frontend

# Copy package.json & package-lock.json and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY frontend/. ./

# Build React app
RUN npm run build

# Install serve to run the production build
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start the app
CMD ["serve", "-s", "build", "-l", "3000"]

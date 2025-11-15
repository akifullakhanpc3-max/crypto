FROM node:18-alpine

WORKDIR /app

# Copy only frontend package management files
COPY frontend/package*.json ./ 

# Install dependencies
RUN npm install

# Copy actual frontend source
COPY frontend/

# Build the app
RUN npm run build

# Install serve to run production
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Run production build
CMD ["serve", "-s", "build", "-l", "3000"]

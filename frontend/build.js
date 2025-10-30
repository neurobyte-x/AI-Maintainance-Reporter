#!/usr/bin/env node
import { build } from 'vite'

build().catch((error) => {
  console.error('Build failed:', error)
  process.exit(1)
})

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import WineList from '../../components/WineList';
import { wineService } from '../../services/api';

// Mock the API service
jest.mock('../../services/api', () => ({
    wineService: {
        getWines: jest.fn()
    }
}));

const mockWines = [
    {
        id: 1,
        name: 'Test Wine 1',
        variety: 'Red',
        region: 'Napa Valley',
        country: 'USA',
        vintage: '2020',
        rating: 4.5
    },
    {
        id: 2,
        name: 'Test Wine 2',
        variety: 'White',
        region: 'Bordeaux',
        country: 'France',
        vintage: '2019',
        rating: 4.0
    }
];

describe('WineList Component', () => {
    beforeEach(() => {
        wineService.getWines.mockResolvedValue({ data: mockWines });
    });

    test('renders wine list with filters', () => {
        render(
            <BrowserRouter>
                <WineList />
            </BrowserRouter>
        );

        // Check if filters are rendered
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/price range/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/search/i)).toBeInTheDocument();
    });

    test('loads and displays wines', async () => {
        render(
            <BrowserRouter>
                <WineList />
            </BrowserRouter>
        );

        // Wait for loading to complete
        await waitFor(() => {
            expect(screen.getByText('Test Wine 1')).toBeInTheDocument();
            expect(screen.getByText('Test Wine 2')).toBeInTheDocument();
        });
    });

    test('handles filter changes', async () => {
        render(
            <BrowserRouter>
                <WineList />
            </BrowserRouter>
        );

        // Change category filter
        const categorySelect = screen.getByLabelText(/category/i);
        fireEvent.change(categorySelect, { target: { value: 'red' } });

        // Check if API was called with new filter
        await waitFor(() => {
            expect(wineService.getWines).toHaveBeenCalledWith(
                expect.objectContaining({ category: 'red' })
            );
        });
    });

    test('handles search', async () => {
        render(
            <BrowserRouter>
                <WineList />
            </BrowserRouter>
        );

        // Fill in search input
        const searchInput = screen.getByLabelText(/search/i);
        fireEvent.change(searchInput, { target: { value: 'test' } });

        // Submit search
        const searchForm = searchInput.closest('form');
        fireEvent.submit(searchForm);

        // Check if API was called with search term
        await waitFor(() => {
            expect(wineService.getWines).toHaveBeenCalledWith(
                expect.objectContaining({ search: 'test' })
            );
        });
    });

    test('displays error message when API call fails', async () => {
        wineService.getWines.mockRejectedValueOnce(new Error('API Error'));

        render(
            <BrowserRouter>
                <WineList />
            </BrowserRouter>
        );

        await waitFor(() => {
            expect(screen.getByText(/failed to load wines/i)).toBeInTheDocument();
        });
    });

    test('displays no results message when no wines found', async () => {
        wineService.getWines.mockResolvedValueOnce({ data: [] });

        render(
            <BrowserRouter>
                <WineList />
            </BrowserRouter>
        );

        await waitFor(() => {
            expect(screen.getByText(/no wines found matching your criteria/i)).toBeInTheDocument();
        });
    });
}); 
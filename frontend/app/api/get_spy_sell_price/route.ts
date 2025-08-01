import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const amount = searchParams.get('amount')
    
    if (!amount || isNaN(Number(amount))) {
      return NextResponse.json(
        { error: 'Invalid amount parameter' }, 
        { status: 400 }
      )
    }

    // For sell price, we'd typically call a different endpoint or calculate differently
    // For now, using the same endpoint but you might want to create a separate one
    const response = await fetch(`http://127.0.0.1:8000/api/get_spy_sell_price?amount=${amount}`)
    
    if (!response.ok) {
      // If sell price endpoint doesn't exist, fall back to buy price for now
      const fallbackResponse = await fetch(`http://127.0.0.1:8000/api/get_spy_price?amount=${amount}`)
      if (fallbackResponse.ok) {
        const data = await fallbackResponse.json()
        return NextResponse.json(data)
      }
      throw new Error('Backend API call failed')
    }
    
    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('Error fetching SPY sell price:', error)
    return NextResponse.json(
      { error: 'Failed to fetch SPY sell price' }, 
      { status: 500 }
    )
  }
}

pragma solidity >=0.4.11 <0.7.0;

contract TakiCoin_ICO {
    uint public max_tcoin = 100000; // Total TakiCoin for sale.
    uint public inr_tcoin = 1000;    //convert rate of 1 TakiCoin to indian rupee.
    uint public total_bought = 0;   // total coin bought by investors.
    
    mapping(address=>uint)equity_tcoin; //mapping equity for TakiCoin.
    mapping(address=>uint)equity_inr;  //mapping equity for TakiCoin-INR.
    
    //check condition that investors can buy TakiCoin
    modifier can_buy_tcoin(uint inr_invest){
        require(inr_invest*inr_tcoin+total_bought<=max_tcoin);
        _;
    }
    
    //get the equity in TakiCoin of investor.
    function equity_in_tcoin(address investor) external view returns(uint){
        return equity_tcoin[investor];
    }
    
    //get the equity in INR of investor.
    function equity_in_inr(address investor) external view returns(uint){
        return equity_inr[investor];
    }    
    
    // Buy TakiCoin.
    function buy_tcoin(address investor, uint inr_invest) external can_buy_tcoin(inr_invest){
        uint tcoin_bought = inr_invest * inr_tcoin;
        equity_tcoin[investor] += tcoin_bought;
        
        equity_inr[investor] = equity_tcoin[investor] / inr_tcoin;
        
        total_bought += tcoin_bought;
    }
    
    // Sell TakiCoin.
    function sell_tcoin(address investor, uint tcoin_sell) external {
        
        equity_tcoin[investor] -= tcoin_sell;
        
        equity_inr[investor] = equity_tcoin[investor] / inr_tcoin;
        
        total_bought -= tcoin_sell;
    }    
}
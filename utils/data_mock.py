"""
Mock data module for competitor analysis system.

This module provides mock competitor data for testing and demonstration purposes.
It includes predefined data for multiple product categories with realistic attributes.
"""

from typing import List, Dict, Any


# Mock competitor database organized by product category
MOCK_COMPETITOR_DATABASE = {
    "手机": [
        {
            "name": "iPhone 15 Pro",
            "company": "Apple",
            "features": ["5G网络", "A17芯片", "钛金属边框", "动态岛", "三摄系统"],
            "price": 7999.0,
            "rating": 4.8
        },
        {
            "name": "华为Mate 60 Pro",
            "company": "华为",
            "features": ["5G网络", "麒麟9000S", "卫星通话", "昆仑玻璃", "三摄系统"],
            "price": 6999.0,
            "rating": 4.7
        },
        {
            "name": "小米14 Pro",
            "company": "小米",
            "features": ["5G网络", "骁龙8 Gen3", "徕卡光学", "2K屏幕", "120W快充"],
            "price": 4999.0,
            "rating": 4.6
        },
        {
            "name": "三星Galaxy S24 Ultra",
            "company": "三星",
            "features": ["5G网络", "骁龙8 Gen3", "S Pen", "AI功能", "200MP相机"],
            "price": 8999.0,
            "rating": 4.7
        },
        {
            "name": "OPPO Find X7 Ultra",
            "company": "OPPO",
            "features": ["5G网络", "骁龙8 Gen3", "哈苏影像", "潜望长焦", "100W快充"],
            "price": 5999.0,
            "rating": 4.5
        }
    ],
    
    "笔记本电脑": [
        {
            "name": "MacBook Pro 16",
            "company": "Apple",
            "features": ["M3 Max芯片", "16英寸显示屏", "长续航", "Retina显示", "雷雳4接口"],
            "price": 19999.0,
            "rating": 4.9
        },
        {
            "name": "ThinkPad X1 Carbon",
            "company": "联想",
            "features": ["英特尔i7", "14英寸屏幕", "轻薄便携", "指纹识别", "军工品质"],
            "price": 12999.0,
            "rating": 4.6
        },
        {
            "name": "Dell XPS 15",
            "company": "戴尔",
            "features": ["英特尔i9", "15.6英寸4K屏", "独立显卡", "窄边框", "高性能"],
            "price": 15999.0,
            "rating": 4.7
        },
        {
            "name": "华为MateBook X Pro",
            "company": "华为",
            "features": ["英特尔i7", "14.2英寸触控屏", "多屏协同", "轻薄设计", "快速充电"],
            "price": 10999.0,
            "rating": 4.5
        }
    ],
    
    "耳机": [
        {
            "name": "AirPods Pro 2",
            "company": "Apple",
            "features": ["主动降噪", "空间音频", "H2芯片", "无线充电", "防水防汗"],
            "price": 1899.0,
            "rating": 4.7
        },
        {
            "name": "索尼WH-1000XM5",
            "company": "索尼",
            "features": ["主动降噪", "LDAC高清音质", "30小时续航", "多点连接", "舒适佩戴"],
            "price": 2399.0,
            "rating": 4.8
        },
        {
            "name": "华为FreeBuds Pro 3",
            "company": "华为",
            "features": ["主动降噪", "Hi-Res音质", "IP54防水", "多设备切换", "无线充电"],
            "price": 1399.0,
            "rating": 4.5
        },
        {
            "name": "Bose QuietComfort Ultra",
            "company": "Bose",
            "features": ["主动降噪", "空间音频", "24小时续航", "舒适设计", "语音清晰"],
            "price": 2799.0,
            "rating": 4.6
        },
        {
            "name": "小米Buds 5 Pro",
            "company": "小米",
            "features": ["主动降噪", "Hi-Res音质", "长续航", "低延迟", "触控操作"],
            "price": 799.0,
            "rating": 4.4
        }
    ],
    
    "平板电脑": [
        {
            "name": "iPad Pro 12.9",
            "company": "Apple",
            "features": ["M2芯片", "12.9英寸屏幕", "120Hz刷新率", "Face ID", "Apple Pencil支持"],
            "price": 9999.0,
            "rating": 4.8
        },
        {
            "name": "三星Galaxy Tab S9 Ultra",
            "company": "三星",
            "features": ["骁龙8 Gen2", "14.6英寸AMOLED", "S Pen", "防水设计", "多任务处理"],
            "price": 8999.0,
            "rating": 4.6
        },
        {
            "name": "华为MatePad Pro 13.2",
            "company": "华为",
            "features": ["麒麟9000S", "13.2英寸OLED", "M-Pencil", "多屏协同", "HarmonyOS"],
            "price": 5999.0,
            "rating": 4.5
        }
    ],
    
    "智能手表": [
        {
            "name": "Apple Watch Ultra 2",
            "company": "Apple",
            "features": ["钛金属表壳", "双频GPS", "潜水功能", "长续航", "健康监测"],
            "price": 6299.0,
            "rating": 4.7
        },
        {
            "name": "华为Watch GT 4",
            "company": "华为",
            "features": ["超长续航", "健康监测", "运动模式", "蓝宝石镜面", "NFC支付"],
            "price": 1688.0,
            "rating": 4.6
        },
        {
            "name": "小米Watch S3",
            "company": "小米",
            "features": ["HyperOS系统", "独立通话", "健康监测", "运动追踪", "长续航"],
            "price": 1299.0,
            "rating": 4.4
        },
        {
            "name": "三星Galaxy Watch 6",
            "company": "三星",
            "features": ["Wear OS", "健康传感器", "旋转表圈", "无线充电", "防水50米"],
            "price": 2499.0,
            "rating": 4.5
        }
    ]
}


# Default competitors for unknown keywords
DEFAULT_COMPETITORS = [
    {
        "name": "产品A",
        "company": "公司A",
        "features": ["功能1", "功能2", "功能3"],
        "price": 1999.0,
        "rating": 4.3
    },
    {
        "name": "产品B",
        "company": "公司B",
        "features": ["功能1", "功能3", "功能4"],
        "price": 2499.0,
        "rating": 4.5
    },
    {
        "name": "产品C",
        "company": "公司C",
        "features": ["功能2", "功能4", "功能5"],
        "price": 2999.0,
        "rating": 4.4
    }
]


def get_mock_competitors(keyword: str) -> List[Dict[str, Any]]:
    """
    Get mock competitor data for a specific product category keyword.
    
    Args:
        keyword: Product category keyword (e.g., "手机", "笔记本电脑", "耳机")
        
    Returns:
        List of competitor dictionaries with the following structure:
        [
            {
                "name": str,           # Product name
                "company": str,        # Company name
                "features": List[str], # List of product features
                "price": float,        # Product price (positive value)
                "rating": float        # Product rating (0.0 - 5.0)
            },
            ...
        ]
        
        Returns 3-5 competitors depending on the category.
        If keyword is not found in database, returns default competitors.
    
    Examples:
        >>> competitors = get_mock_competitors("手机")
        >>> len(competitors)
        5
        >>> competitors[0]["name"]
        'iPhone 15 Pro'
        
        >>> competitors = get_mock_competitors("unknown")
        >>> len(competitors)
        3
    """
    # Normalize keyword by stripping whitespace
    keyword = keyword.strip() if keyword else ""
    
    # Look up keyword in mock database
    if keyword in MOCK_COMPETITOR_DATABASE:
        return MOCK_COMPETITOR_DATABASE[keyword]
    
    # Return default competitors for unknown keywords
    return DEFAULT_COMPETITORS


def get_default_competitors() -> List[Dict[str, Any]]:
    """
    Get default fallback competitors for unknown or empty keywords.
    
    Returns:
        List of 3 default competitor dictionaries with generic data.
        
    Examples:
        >>> competitors = get_default_competitors()
        >>> len(competitors)
        3
        >>> competitors[0]["name"]
        '产品A'
    """
    return DEFAULT_COMPETITORS


def get_all_categories() -> List[str]:
    """
    Get all available product categories in the mock database.
    
    Returns:
        List of category keywords available in the database.
        
    Examples:
        >>> categories = get_all_categories()
        >>> "手机" in categories
        True
        >>> "笔记本电脑" in categories
        True
    """
    return list(MOCK_COMPETITOR_DATABASE.keys())

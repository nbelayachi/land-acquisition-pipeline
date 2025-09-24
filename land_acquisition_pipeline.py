# -*- coding: utf-8 -*-
"""
Enhanced Land Acquisition Pipeline with Geocoding Integration and Funnel Metrics
Handles complete workflow from single input file to municipality-structured outputs
ENHANCED: Automatic geocoding, PEC email retrieval, and comprehensive funnel tracking
VERSION: 2.9.7 (with parcel ownership grouping analysis)

@author: Optimized for CP-Municipality land acquisition workflow with address enhancement
"""

import pandas as pd
import requests
import json
import time
import logging
import re
import os
import pickle
import shutil
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

class IntegratedLandAcquisitionPipeline:
    def __init__(self, config_file="land_acquisition_config.json"):
        """Initialize the integrated pipeline with configuration and geocoding"""
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.setup_directories()
        self.load_cache()
        self.campaign_stats = self.init_campaign_stats()
        
        # Initialize integrated features
        self.init_geocoding()
        self.init_pec_integration()
        
        # Set simple defaults
        self.municipality_batch_size = 50
        self.validation_quality_threshold = 70
        
    def init_geocoding(self):
        """Initialize geocoding functionality"""
        geocoding_config = self.config.get("geocoding_settings", {})
        self.geocoding_enabled = geocoding_config.get("enabled", False)
        self.geocoding_token = geocoding_config.get("token", "")
        
        if self.geocoding_enabled and self.geocoding_token and self.geocoding_token != "YOUR_GEOCODING_TOKEN_HERE":
            self.logger.info("Geocoding enhancement enabled")
            print("🗺️  Geocoding enhancement enabled - addresses will be enhanced with ZIP codes and coordinates")
            self.load_geocoding_cache()
            self.geocoding_sleep = geocoding_config.get("sleep_between_calls", 2)
            self.geocoding_recovery_enabled = geocoding_config.get("timeout_recovery_enabled", True)
        else:
            self.geocoding_enabled = False
            if not self.geocoding_token or self.geocoding_token == "YOUR_GEOCODING_TOKEN_HERE":
                self.logger.warning("Geocoding disabled: No valid geocoding token provided")
                print("⚠️  Geocoding disabled: No valid geocoding token provided")
            else:
                self.logger.info("Geocoding disabled in configuration")
                print("📍 Geocoding disabled in configuration")

    def init_pec_integration(self):
        """Initialize PEC email integration functionality"""
        pec_config = self.config.get("pec_integration", {})
        self.pec_enabled = pec_config.get("enabled", False)
        self.pec_token = pec_config.get("token", "")

        if self.pec_enabled and self.pec_token and self.pec_token != "YOUR_PEC_API_TOKEN":
            self.logger.info("PEC email integration enabled")
            print("📧 PEC email integration for companies enabled")
            self.load_pec_cache()
            self.pec_sleep = pec_config.get("sleep_between_calls", 1)
        else:
            self.pec_enabled = False
            if not self.pec_token or self.pec_token == "YOUR_PEC_API_TOKEN":
                 self.logger.warning("PEC integration disabled: No valid PEC token provided")
                 print("⚠️  PEC integration disabled: No valid PEC token provided")
            else:
                self.logger.info("PEC integration disabled in configuration")
                print("📧 PEC email integration disabled in configuration")

    def load_geocoding_cache(self):
        """Load geocoding cache"""
        cache_dir = self.config.get("cache_directory", "cache")
        geocoding_cache_file = os.path.join(cache_dir, "geocoding_cache.pkl")
        if os.path.exists(geocoding_cache_file):
            with open(geocoding_cache_file, 'rb') as f:
                self.geocoding_cache = pickle.load(f)
            self.logger.info(f"Loaded {len(self.geocoding_cache)} cached geocoding responses")
        else:
            self.geocoding_cache = {}
    
    def save_geocoding_cache(self):
        """Save geocoding cache"""
        cache_dir = self.config.get("cache_directory", "cache")
        geocoding_cache_file = os.path.join(cache_dir, "geocoding_cache.pkl")
        with open(geocoding_cache_file, 'wb') as f:
            pickle.dump(self.geocoding_cache, f)

    def load_pec_cache(self):
        """Load PEC cache"""
        cache_dir = self.config.get("cache_directory", "cache")
        pec_cache_file = os.path.join(cache_dir, "pec_cache.pkl")
        if os.path.exists(pec_cache_file):
            with open(pec_cache_file, 'rb') as f:
                self.pec_cache = pickle.load(f)
            self.logger.info(f"Loaded {len(self.pec_cache)} cached PEC responses")
        else:
            self.pec_cache = {}

    def save_pec_cache(self):
        """Save PEC cache"""
        cache_dir = self.config.get("cache_directory", "cache")
        pec_cache_file = os.path.join(cache_dir, "pec_cache.pkl")
        with open(pec_cache_file, 'wb') as f:
            pickle.dump(self.pec_cache, f)
    
    def load_config(self, config_file):
        """Load or create configuration file"""
        default_config = {
            "api_settings": {
                "token": "YOUR_TOKEN_HERE",
                "sleep_between_calls": 2
            },
            "geocoding_settings": {
                "enabled": False,
                "token": "YOUR_GEOCODING_TOKEN_HERE",
                "sleep_between_calls": 2
            },
            "pec_integration": {
                "enabled": False,
                "token": "YOUR_PEC_API_TOKEN"
            },
            "enhanced_classification": {
                "enabled": False,
                "ultra_high_completeness_threshold": 0.75,
                "high_completeness_threshold": 0.5,
                "enable_ultra_high_confidence": True
            },
            "cost_tracking": {
                "method": "manual_balance_check",
                "prompt_for_start_balance": True,
                "prompt_for_end_balance": True
            },
            "output_structure": {
                "local_processing_dir": "local_processing",
                "completed_campaigns_dir": "completed_campaigns",
                "auto_copy_to_onedrive": True
            },
            "timeout_recovery": {
                "enable_recovery": True,
                "recovery_attempts": 30,
                "recovery_delay_seconds": 5,
                "max_recovery_age_hours": 24
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                return config_data.get('land_acquisition_config', default_config)
        else:
            print(f"❌ Configuration file {config_file} not found!")
            return default_config
    
    def get_company_pec(self, cf_piva):
        """
        Retrieve PEC email for a company using its tax code (CF/P.IVA).
        """
        if not self.pec_enabled or not cf_piva:
            return None, 'Disabled'
        
        cache_key = f"pec_{cf_piva}"
        if cache_key in self.pec_cache:
            self.logger.info(f"Using cached PEC for {cf_piva}")
            cached_data = self.pec_cache[cache_key]
            return cached_data.get('pec'), cached_data.get('status', 'cached')

        self.campaign_stats["pec_api_calls"] += 1
        
        url = f"https://company.openapi.com/IT-marketing/{cf_piva}"
        headers = {
            "Authorization": f"Bearer {self.pec_token}"
        }

        try:
            print(f"      📧 Looking up PEC for company {cf_piva}...")
            
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                pec_email = data.get('data', {}).get('pec')
                
                if pec_email:
                    self.logger.info(f"PEC found for {cf_piva}: {pec_email}")
                    status = 'found'
                    self.campaign_stats["pec_found_count"] += 1
                else:
                    self.logger.info(f"PEC not found for {cf_piva}")
                    status = 'not_found'
                
                self.pec_cache[cache_key] = {"pec": pec_email, "status": status}
                self.save_pec_cache()
                return pec_email, status
            
            elif response.status_code == 401:
                self.logger.error(f"PEC lookup failed for {cf_piva} with status 401. This indicates an invalid or expired token for the company.openapi.com service.")
                return None, 'error_401_invalid_token'
                
            else:
                self.logger.error(f"PEC lookup failed for {cf_piva} with status {response.status_code}")
                self.pec_cache[cache_key] = {"pec": None, "status": f'error_{response.status_code}'}
                self.save_pec_cache()
                return None, f'error_{response.status_code}'

        except Exception as e:
            self.logger.error(f"PEC lookup exception for {cf_piva}: {str(e)}")
            return None, 'exception'

    def get_zip_code_from_address(self, address, token):
        """
        Get ZIP code and geocoding data from address using geocoding API
        """
        if not address or pd.isna(address) or str(address).strip() == "":
            return None, "Empty address", None
        
        address = str(address).strip()
        self.campaign_stats["geocoding_api_calls"] += 1
        
        self.logger.info(f"Geocoding address: {address}")
        
        cache_key = f"geocode_{address}"
        if cache_key in self.geocoding_cache:
            cached_result = self.geocoding_cache[cache_key]
            if cached_result.get("postal_code"):
                self.logger.info(f"Using cached ZIP code for: {address}")
                return cached_result["postal_code"], "cached", cached_result.get("geocoding_data")
            else:
                self.logger.info(f"Using cached 'no ZIP' result for: {address}")
                return None, cached_result.get("error", "cached_no_zip"), None
        
        url = "https://geocoding.openapi.it/geocode"
        headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        payload = {"address": address}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            self.logger.info(f"Geocoding API response status: {response.status_code}")
            
            if response.status_code == 401:
                error_msg = "Invalid_Geocoding_Token"
                self.logger.error(f"Geocoding API authentication failed - check your geocoding token")
                self.geocoding_cache[cache_key] = {"postal_code": None, "geocoding_data": None, "error": error_msg}
                self.save_geocoding_cache()
                return None, error_msg, None
            
            if response.status_code != 200:
                error_msg = f"Geocoding_Error_{response.status_code}"
                self.logger.error(f"Geocoding API failed with status {response.status_code}")
                self.geocoding_cache[cache_key] = {"postal_code": None, "geocoding_data": None, "error": error_msg}
                self.save_geocoding_cache()
                return None, error_msg, None
            
            response_data = response.json()
            self.logger.info(f"Geocoding API response structure: {list(response_data.keys())}")
            
            if response_data.get('success') == True and response_data.get('element'):
                element = response_data['element']
                postal_code = element.get('postalCode')
                
                if postal_code and postal_code != "null":
                    geocoding_data = self.extract_geocoding_data(element)
                    if geocoding_data:
                        self.logger.info(f"Successfully extracted geocoding data with {len(geocoding_data)} fields")
                        geocoding_data['postal_code'] = postal_code
                    
                    self.logger.info(f"Direct geocoding success: {address} -> {postal_code}")
                    cache_entry = {"postal_code": postal_code, "geocoding_data": geocoding_data, "error": None}
                    self.geocoding_cache[cache_key] = cache_entry
                    self.save_geocoding_cache()
                    
                    return postal_code, "success", geocoding_data
                else:
                    self.logger.info(f"Direct geocoding - no postal code: {address}")
                    self.geocoding_cache[cache_key] = {"postal_code": None, "geocoding_data": None, "error": "no_postal_code"}
                    self.save_geocoding_cache()
                    return None, "no_postal_code", None
            
            request_id = response_data.get('data', {}).get('id')
            if not request_id:
                self.logger.warning(f"No request ID found for geocoding: {address}")
                
                if response_data.get('success') == False:
                    error_msg = "Geocoding_API_returned_success_false"
                    self.geocoding_cache[cache_key] = {"postal_code": None, "geocoding_data": None, "error": error_msg}
                    self.save_geocoding_cache()
                    return None, error_msg, None
                
                self.geocoding_cache[cache_key] = {"postal_code": None, "geocoding_data": None, "error": "unexpected_format"}
                self.save_geocoding_cache()
                return None, "unexpected_format", None
            
            timeout_key = f"timeout_geocode_{request_id}"
            recovery_data = {
                "request_id": request_id,
                "address": address,
                "timestamp": datetime.now().isoformat(),
                "cache_key": cache_key,
                "status": "pending"
            }
            self.geocoding_cache[timeout_key] = recovery_data
            self.save_geocoding_cache()
            self.logger.info(f"🆔 Geocoding request ID saved for potential recovery: {request_id}")
            
            status_url = f"https://geocoding.openapi.it/richiesta/{request_id}"
            max_attempts = 60
            
            for attempt in range(max_attempts):
                print(f"  [Geocoding API] Attempt {attempt+1}/{max_attempts} for: {address[:50]}...")
                self.logger.info(f"Geocoding attempt {attempt+1}/{max_attempts}")
                
                status_response = requests.get(status_url, headers=headers)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    if (status_data.get('data', {}).get('risultato') and 
                        status_data['data']['risultato'].get('elements')):
                        
                        element = status_data['data']['risultato']['elements'].get('element', {})
                        postal_code = element.get('postalCode')
                        
                        if postal_code and postal_code != "null":
                            geocoding_data = self.extract_geocoding_data(element)
                            geocoding_data['postal_code'] = postal_code
                            
                            self.geocoding_cache.pop(timeout_key, None)
                            self.geocoding_cache[cache_key] = {"postal_code": postal_code, "geocoding_data": geocoding_data, "error": None}
                            self.save_geocoding_cache()
                            self.logger.info(f"ASYNC GEOCODING SUCCESS - Request ID {request_id} completed: {address} -> {postal_code}")
                            return postal_code, "success", geocoding_data
                        else:
                            self.geocoding_cache.pop(timeout_key, None)
                            self.geocoding_cache[cache_key] = {"postal_code": None, "geocoding_data": None, "error": "no_postal_code"}
                            self.save_geocoding_cache()
                            self.logger.info(f"ASYNC GEOCODING COMPLETED (No ZIP) - Request ID {request_id}: {address}")
                            return None, "no_postal_code", None
                    
                    if status_data.get('data', {}).get('stato') in ['evasa', 'completato']:
                        self.geocoding_cache.pop(timeout_key, None)
                        self.geocoding_cache[cache_key] = {"postal_code": None, "geocoding_data": None, "error": "completed_no_data"}
                        self.save_geocoding_cache()
                        self.logger.info(f"ASYNC GEOCODING COMPLETED (No Data) - Request ID {request_id}: {address}")
                        return None, "completed_no_data", None
                
                time.sleep(3)
            
            recovery_data["status"] = "timeout"
            recovery_data["timeout_timestamp"] = datetime.now().isoformat()
            self.geocoding_cache[timeout_key] = recovery_data
            self.save_geocoding_cache()
            
            self.campaign_stats["geocoding_timeout_requests"] += 1
            
            self.logger.warning(f"⏰ GEOCODING TIMEOUT - Request ID {request_id} saved for recovery: {address}")
            
            return None, f"Geocoding_Timeout_RequestID_{request_id}", None
            
        except Exception as e:
            self.logger.error(f"Geocoding exception for '{address}': {str(e)}")
            self.geocoding_cache[cache_key] = {"postal_code": None, "geocoding_data": None, "error": f"Exception: {str(e)[:50]}"}
            self.save_geocoding_cache()
            return None, f"Geocoding_Error: {str(e)[:50]}", None
    
    def extract_geocoding_data(self, element):
        """Extract all geocoding data from API response element"""
        try:
            self.logger.info(f"Extracting geocoding data from element: {list(element.keys())}")
            
            admin_levels = element.get('adminLevels', {})
            province_info = {}
            region_info = {}
            
            if admin_levels:
                for key in ['1', 1]:
                    if key in admin_levels:
                        region_info = admin_levels[key]
                        break
                for key in ['2', 2]:
                    if key in admin_levels:
                        province_info = admin_levels[key]
                        break
            
            street_name = element.get('streetName', '')
            street_number = element.get('streetNumber', '')
            postal_code = element.get('postalCode', '')
            city = element.get('locality', '')
            province_code = province_info.get('code', '') if province_info else ''
            
            address_parts = []
            if street_name and street_number:
                address_parts.append(f"{street_name}, {street_number}")
            elif street_name:
                address_parts.append(street_name)
            
            if postal_code and city and province_code:
                address_parts.append(f"{postal_code} {city} {province_code}")
            elif postal_code and city:
                address_parts.append(f"{postal_code} {city}")
            
            italian_address = ", ".join(address_parts)
            
            geocoding_data = {
                'italian_address': italian_address,
                'street_name': street_name,
                'street_number': street_number,
                'postal_code': postal_code,
                'city': city,
                'province_name': province_info.get('name', '') if province_info else '',
                'province_code': province_code,
                'region': region_info.get('name', '') if region_info else '',
                'sub_locality': element.get('subLocality') or '',
                'country': element.get('country', ''),
                'country_code': element.get('countryCode', ''),
                'latitude': element.get('latitude'),
                'longitude': element.get('longitude'),
                'geocoding_provider': element.get('providedBy', ''),
                'geocoding_id': element.get('id', '')
            }
            
            self.logger.info(f"Successfully extracted {len(geocoding_data)} geocoding fields")
            return geocoding_data
            
        except Exception as e:
            self.logger.error(f"Error extracting geocoding data: {str(e)}")
            return None
    
    def enhance_addresses_with_geocoding(self, df):
        """
        Enhance addresses with geocoding data using cleaned_ubicazione column
        """
        if not self.geocoding_enabled:
            return df
        if 'cleaned_ubicazione' not in df.columns:
            return df
        
        print(f"   🗺️  Enhancing addresses with geocoding data...")
        
        geocoding_columns = [
            'Poste_Address', 'Geocoding_Status', 'Geocoded_Address_Italian',
            'Street_Name', 'Street_Number', 'Postal_Code', 'City', 
            'Province_Name', 'Province_Code', 'Region', 'Sub_Locality', 
            'Country', 'Country_Code', 'Latitude', 'Longitude', 
            'Geocoding_Provider', 'Geocoding_ID'
        ]
        
        for col in geocoding_columns:
            df[col] = None
        
        unique_addresses = df['cleaned_ubicazione'].dropna().unique()
        address_to_data = {}
        print(f"      🎯 Processing {len(unique_addresses)} unique addresses...")
        
        processed_count = 0
        successful_geocodes = 0
        
        for address in unique_addresses:
            if pd.isna(address) or str(address).strip() == "":
                continue
            processed_count += 1
            if processed_count % 5 == 0:
                print(f"      📍 Geocoding progress: {processed_count}/{len(unique_addresses)} ({(processed_count / len(unique_addresses)) * 100:.1f}%)")
            
            zip_code, status, geocoding_data = self.get_zip_code_from_address(address, self.geocoding_token)
            
            if zip_code and geocoding_data:
                address_to_data[address] = {'zip_code': zip_code, 'status': 'Success', 'geocoding_data': geocoding_data}
                successful_geocodes += 1
                self.campaign_stats["successful_geocodes"] += 1
            else:
                address_to_data[address] = {'zip_code': None, 'status': status, 'geocoding_data': None}
            
            time.sleep(self.geocoding_sleep)
        
        print(f"      📋 Applying geocoding results to dataframe...")
        rich_data_count = 0
        
        for index, row in df.iterrows():
            address = row['cleaned_ubicazione']
            if pd.notna(address) and address in address_to_data:
                data = address_to_data[address]
                df.at[index, 'Poste_Address'] = data['zip_code']
                df.at[index, 'Geocoding_Status'] = data['status']
                
                geocoding_data = data.get('geocoding_data')
                if geocoding_data and isinstance(geocoding_data, dict):
                    try:
                        for key, value in geocoding_data.items():
                            col_name = key.replace('_', ' ').title().replace(' ', '_')
                            if col_name in geocoding_columns:
                                df.at[index, col_name] = value
                        df.at[index, 'Geocoded_Address_Italian'] = geocoding_data.get('italian_address', '') # explicit mapping
                        rich_data_count += 1
                    except Exception as e:
                        self.logger.error(f"Error applying geocoding data for {address}: {str(e)}")
            else:
                df.at[index, 'Geocoding_Status'] = 'Empty Address'
        
        self.campaign_stats["addresses_geocoded"] += len(unique_addresses)
        self.campaign_stats["addresses_with_rich_data"] += rich_data_count
        
        success_rate = (successful_geocodes / len(unique_addresses) * 100) if unique_addresses.size > 0 else 0
        print(f"      ✅ Geocoding complete: {successful_geocodes}/{len(unique_addresses)} addresses ({success_rate:.1f}% success)")
        return df
    
    def recover_geocoding_timeout_requests(self):
        """
        Attempt to recover data from timed-out geocoding requests
        """
        if not self.geocoding_enabled or not self.geocoding_recovery_enabled:
            return
        
        print(f"\n🔄 GEOCODING TIMEOUT RECOVERY SYSTEM")
        
        timeout_entries = {k: v for k, v in self.geocoding_cache.items() 
                          if k.startswith("timeout_geocode_") and isinstance(v, dict) and v.get("status") in ["pending", "timeout"]}
        
        if not timeout_entries:
            print("   ✅ No geocoding timeout requests found")
            return
            
        print(f"   🔍 Found {len(timeout_entries)} geocoding timeout requests to check")
        
        recovery_config = self.config.get("geocoding_settings", {})
        max_recovery_attempts = recovery_config.get("max_recovery_attempts", 30)
        recovery_delay = recovery_config.get("recovery_delay_seconds", 5)
        max_age_hours = recovery_config.get("max_recovery_age_hours", 24)
        
        recovered_count = 0
        
        for timeout_key, recovery_data in timeout_entries.items():
            request_id = recovery_data["request_id"]
            address = recovery_data["address"]
            timestamp_str = recovery_data.get("timeout_timestamp", recovery_data.get("timestamp"))
            
            try:
                request_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00').replace('+00:00', ''))
                age_hours = (datetime.now() - request_time).total_seconds() / 3600
                if age_hours > max_age_hours:
                    continue
            except Exception as e:
                self.logger.warning(f"Could not parse geocoding timestamp for {request_id}: {e}")
            
            print(f"   🔄 Checking geocoding {request_id[:8]}... ({address[:30]}...)", end="")
            
            status_url = f"https://geocoding.openapi.it/richiesta/{request_id}"
            headers = {"content-type": "application/json", "Authorization": f"Bearer {self.geocoding_token}"}
            
            try:
                for attempt in range(max_recovery_attempts):
                    self.campaign_stats["geocoding_recovery_attempts"] += 1
                    status_response = requests.get(status_url, headers=headers)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if (status_data.get('data', {}).get('risultato') and status_data['data']['risultato'].get('elements')):
                            element = status_data['data']['risultato']['elements'].get('element', {})
                            postal_code = element.get('postalCode')
                            if postal_code and postal_code != "null":
                                geocoding_data = self.extract_geocoding_data(element)
                                geocoding_data['postal_code'] = postal_code
                                cache_key = recovery_data["cache_key"]
                                self.geocoding_cache[cache_key] = {"postal_code": postal_code, "geocoding_data": geocoding_data, "error": None}
                                self.geocoding_cache.pop(timeout_key, None)
                                recovered_count += 1
                                self.campaign_stats["successful_geocoding_recoveries"] += 1
                                print(f" ✅ RECOVERED! ZIP: {postal_code}")
                                break
                            else:
                                cache_key = recovery_data["cache_key"]
                                self.geocoding_cache[cache_key] = {"postal_code": None, "geocoding_data": None, "error": "no_postal_code"}
                                self.geocoding_cache.pop(timeout_key, None)
                                print(f" ✅ No ZIP available")
                                break
                        elif status_data.get('data', {}).get('stato') in ['evasa', 'completato']:
                            cache_key = recovery_data["cache_key"]
                            self.geocoding_cache[cache_key] = {"postal_code": None, "geocoding_data": None, "error": "completed_no_data"}
                            self.geocoding_cache.pop(timeout_key, None)
                            print(f" ✅ No data available")
                            break
                    if attempt < max_recovery_attempts - 1:
                        time.sleep(recovery_delay)
                else:
                    print(f" ⏳ Still processing")
            except Exception as e:
                print(f" ❌ Error: {str(e)}")
        
        self.save_geocoding_cache()
    
    def create_powerbi_export(self, campaign_name, campaign_dir):
        """Create Power BI export data with ENHANCED business intelligence metrics and funnel data"""
        print(f"🔍 DEBUG: PowerBI export called - Campaign: {campaign_name}")
        print(f"  Campaign dir: {campaign_dir}")
        print(f"  Campaign stats available: {bool(self.campaign_stats)}")
        print(f"  Municipalities processed: {len(self.campaign_stats.get('municipalities_processed', {}))}")
        
        powerbi_data = []
        
        for municipality_key, stats in self.campaign_stats.get('municipalities_processed', {}).items():
            summary_metrics = stats.get("summary_metrics", {})
            municipality_record = {
                "Campaign_Date": datetime.now().strftime("%Y-%m-%d"),
                "Campaign_Name": campaign_name,
                "Municipality_Key": municipality_key,
                "CP": stats.get("CP", municipality_key.split('_')[0]),
                "Municipality": stats.get("comune", '_'.join(municipality_key.split('_')[1:]).replace('_', ' ')),

                # Existing metrics
                "Input_Parcels": summary_metrics.get("Input_Parcels", 0),
                "Property_Data_Retrieved_Rate": summary_metrics.get("Property_Data_Retrieved_Rate", 0.0),
                "Individual_Landowners_Found": summary_metrics.get("Individual_Landowners_Found", 0),
                "Unique_Company_Owners": summary_metrics.get("Unique_Company_Owners", 0),
                # REVISED v2.9.2
                "Unique_Owner_Address_Pairs": summary_metrics.get("Unique_Owner_Address_Pairs", 0),
                "Direct_Mail_Final_Contacts": summary_metrics.get("Direct_Mail_Final_Contacts", 0),
                "Direct_Mail_Final_Area_Ha": summary_metrics.get("Direct_Mail_Final_Area_Ha", 0),
                "Agency_Final_Contacts": summary_metrics.get("Agency_Final_Contacts", 0),
                "Agency_Final_Area_Ha": summary_metrics.get("Agency_Final_Area_Ha", 0),

                # Cost tracking
                "Campaign_Cost": self.campaign_stats.get("campaign_cost", 0.0),
                "Timeout_Requests": self.campaign_stats.get("timeout_requests", 0),
                "Successful_Recoveries": self.campaign_stats.get("successful_recoveries", 0),
                "Recovery_Cost_Saved": self.campaign_stats.get("recovery_cost_saved", 0.0)
            }
            powerbi_data.append(municipality_record)
        
        if powerbi_data:
            powerbi_df = pd.DataFrame(powerbi_data)
            powerbi_file = os.path.join(campaign_dir, "PowerBI_Dataset.csv")
            powerbi_df.to_csv(powerbi_file, index=False, encoding='utf-8-sig')
            print(f"   📊 Power BI dataset created with enhanced metrics and funnel data: {os.path.basename(powerbi_file)}")
            print(f"       Shape: {powerbi_df.shape}, Municipalities: {len(powerbi_data)}")
        else:
            print(f"   ❌ Power BI dataset: No data available for export")

    def create_powerbi_export_from_consolidated_data(self, campaign_name, campaign_dir):
        """Create PowerBI CSV from consolidated Excel data (more reliable than campaign_stats)"""
        print(f"🔍 DEBUG: Creating PowerBI export from consolidated Excel data")
        
        # Read from the consolidated Excel file
        output_file = os.path.join(campaign_dir, f"{campaign_name}_Results.xlsx")
        
        if not os.path.exists(output_file):
            print(f"❌ Excel file not found: {output_file}")
            return
        
        try:
            # Read Campaign_Summary sheet
            df_summary = pd.read_excel(output_file, sheet_name='Campaign_Summary')
            print(f"  Campaign Summary loaded: {df_summary.shape}")
            
            powerbi_data = []
            
            for index, row in df_summary.iterrows():
                # Create PowerBI record from Campaign_Summary data
                record = {
                    # Campaign metadata
                    "Campaign_Date": datetime.now().strftime("%Y-%m-%d"),
                    "Campaign_Name": campaign_name,
                    "Municipality_Key": f"{row['CP']}_{row['comune'].replace(' ', '_')}",
                    "CP": row['CP'],
                    "Municipality": row['comune'],
                    
                    # Core metrics from Campaign_Summary
                    "Input_Parcels": int(row['Input_Parcels']) if pd.notna(row['Input_Parcels']) else 0,
                    "Total_Area_Ha": float(row['Input_Area_Ha']) if pd.notna(row['Input_Area_Ha']) else 0.0,
                    "Property_Data_Retrieved_Rate": float(row['Property_Data_Retrieved_Rate']) if pd.notna(row['Property_Data_Retrieved_Rate']) else 0.0,
                    "Individual_Landowners_Found": int(row['Individual_Landowners_Found']) if pd.notna(row['Individual_Landowners_Found']) else 0,
                    "Unique_Company_Owners": int(row['Unique_Company_Owners']) if pd.notna(row['Unique_Company_Owners']) else 0,
                    "Unique_Owner_Address_Pairs": int(row['Unique_Owner_Address_Pairs']) if pd.notna(row['Unique_Owner_Address_Pairs']) else 0,
                    "Direct_Mail_Final_Contacts": int(row['Direct_Mail_Final_Contacts']) if pd.notna(row['Direct_Mail_Final_Contacts']) else 0,
                    "Agency_Final_Contacts": int(row['Agency_Final_Contacts']) if pd.notna(row['Agency_Final_Contacts']) else 0,
                    "Direct_Mail_Final_Area_Ha": float(row['Direct_Mail_Final_Area_Ha']) if pd.notna(row['Direct_Mail_Final_Area_Ha']) else 0.0,
                    "Agency_Final_Area_Ha": float(row['Agency_Final_Area_Ha']) if pd.notna(row['Agency_Final_Area_Ha']) else 0.0,
                    
                    # Calculated business metrics
                    "Total_Final_Contacts": (int(row['Direct_Mail_Final_Contacts']) if pd.notna(row['Direct_Mail_Final_Contacts']) else 0) + (int(row['Agency_Final_Contacts']) if pd.notna(row['Agency_Final_Contacts']) else 0),
                    "Direct_Mail_Percentage": round((float(row['Direct_Mail_Final_Contacts']) / (float(row['Direct_Mail_Final_Contacts']) + float(row['Agency_Final_Contacts'])) * 100), 1) if (pd.notna(row['Direct_Mail_Final_Contacts']) and pd.notna(row['Agency_Final_Contacts']) and (float(row['Direct_Mail_Final_Contacts']) + float(row['Agency_Final_Contacts'])) > 0) else 0.0,
                    
                    # Additional metrics if available
                    "Residential_Viability_Rate": float(row.get('Residential_Viability_Rate', 0)) if pd.notna(row.get('Residential_Viability_Rate', 0)) else 0.0,
                    "Address_Verification_Rate": float(row.get('Address_Verification_Rate', 0)) if pd.notna(row.get('Address_Verification_Rate', 0)) else 0.0,
                    "Interpolation_Risks_Detected": int(row.get('Interpolation_Risks_Detected', 0)) if pd.notna(row.get('Interpolation_Risks_Detected', 0)) else 0,
                    "Companies_With_PEC": int(row.get('Companies_With_PEC', 0)) if pd.notna(row.get('Companies_With_PEC', 0)) else 0,
                    "PEC_Success_Rate": float(row.get('PEC_Success_Rate', 0)) if pd.notna(row.get('PEC_Success_Rate', 0)) else 0.0
                }
                powerbi_data.append(record)
            
            if powerbi_data:
                # Create DataFrame and export
                powerbi_df = pd.DataFrame(powerbi_data)
                powerbi_file = os.path.join(campaign_dir, "PowerBI_Dataset.csv")
                powerbi_df.to_csv(powerbi_file, index=False, encoding='utf-8-sig')
                print(f"   📊 PowerBI dataset created from Excel data: {os.path.basename(powerbi_file)}")
                print(f"       Shape: {powerbi_df.shape}, Municipalities: {len(powerbi_data)}")
            else:
                print(f"   ❌ No data processed for PowerBI export")
                
        except Exception as e:
            print(f"❌ Error creating PowerBI export: {str(e)}")
            import traceback
            traceback.print_exc()

    def is_province_match(self, original_address, geocoded_province_code):
        """v2.9.1: Helper function to check if geocoded province matches original."""
        if not isinstance(original_address, str) or not isinstance(geocoded_province_code, str):
            return False
        match = re.search(r'\(([A-Z]{2})\)', original_address.upper())
        if match:
            original_province_code = match.group(1)
            return original_province_code == geocoded_province_code.upper()
        return False

    def extract_street_number_enhanced(self, address):
        """
        Enhanced number extraction that correctly handles Italian geocoded addresses
        Fixes the issue where postal codes were extracted instead of street numbers
        """
        if not isinstance(address, str):
            return None
            
        # For Italian geocoded addresses in format: "Street Name, Number, PostalCode City Province"
        # Extract the number that comes AFTER the first comma but BEFORE the postal code
        
        # Try geocoded format first: "Street Name, Number, PostalCode..."
        geocoded_pattern = r',\s*(\d+[A-Za-z/]{0,3})\s*,'
        match = re.search(geocoded_pattern, address)
        if match:
            return match.group(1).upper().strip()
        
        # Original patterns for raw addresses
        patterns = [
            r'n\.?\s*(\d+[A-Za-z/]{0,3})(?!\d)',  # "n. 34" - avoid longer numbers
            r'\b(\d+[A-Za-z/]{0,3})(?:\s+[A-Z]|\s*$)',  # Number followed by letters or end
            r'^.*?(\d+[A-Za-z/]{0,3})(?:\s+\w+)*\s*$'   # Last resort
        ]
        
        for pattern in patterns:
            match = re.search(pattern, address, re.IGNORECASE)
            if match:
                number = match.group(1).upper().strip()
                # Avoid postal codes (usually 5 digits)
                if len(re.sub(r'[A-Z/]', '', number)) < 5:
                    return number
        
        return None
    
    def normalize_number_for_comparison(self, number_str):
        """Normalize number for enhanced comparison"""
        if not number_str:
            return None
            
        num_str = str(number_str).upper().strip()
        base_match = re.match(r'(\d+)', num_str)
        if base_match:
            base_number = base_match.group(1)
            suffix_match = re.search(r'(\d+)([A-Z/]+)', num_str)
            suffix = suffix_match.group(2) if suffix_match else ''
            
            return {
                'full': num_str,
                'base': base_number,
                'suffix': suffix
            }
        return None
    
    def calculate_number_similarity(self, original_num, geocoded_num):
        """Calculate similarity between original and geocoded numbers"""
        if not original_num or not geocoded_num:
            return {'similarity': 0.0, 'match_type': 'no_match', 'confidence': 'LOW', 'reason': 'Missing numbers'}
        
        orig_norm = self.normalize_number_for_comparison(original_num)
        geo_norm = self.normalize_number_for_comparison(geocoded_num)
        
        if not orig_norm or not geo_norm:
            return {'similarity': 0.0, 'match_type': 'no_match', 'confidence': 'LOW', 'reason': 'Invalid numbers'}
        
        # Exact match (including suffixes)
        if orig_norm['full'] == geo_norm['full']:
            return {
                'similarity': 1.0, 
                'match_type': 'exact_match', 
                'confidence': 'ULTRA_HIGH',
                'reason': f"Perfect match: {orig_norm['full']}"
            }
        
        # Base number match (ignoring suffixes)
        if orig_norm['base'] == geo_norm['base']:
            return {
                'similarity': 0.9, 
                'match_type': 'base_match', 
                'confidence': 'HIGH',
                'reason': f"Base number match: {orig_norm['base']} (suffixes: '{orig_norm['suffix']}' vs '{geo_norm['suffix']}')"
            }
        
        # Close numbers
        try:
            orig_int = int(orig_norm['base'])
            geo_int = int(geo_norm['base'])
            diff = abs(orig_int - geo_int)
            
            if diff == 1:
                return {
                    'similarity': 0.7, 
                    'match_type': 'adjacent_number', 
                    'confidence': 'MEDIUM',
                    'reason': f"Adjacent numbers: {orig_int} vs {geo_int}"
                }
            elif diff == 2:
                return {
                    'similarity': 0.6, 
                    'match_type': 'close_number', 
                    'confidence': 'MEDIUM',
                    'reason': f"Close numbers: {orig_int} vs {geo_int}"
                }
            else:
                return {
                    'similarity': 0.1, 
                    'match_type': 'different_number', 
                    'confidence': 'LOW',
                    'reason': f"Different numbers: {orig_int} vs {geo_int}"
                }
                
        except ValueError:
            return {
                'similarity': 0.2, 
                'match_type': 'non_numeric', 
                'confidence': 'LOW',
                'reason': f"Non-numeric comparison"
            }
    
    def assess_address_completeness(self, row):
        """Assess completeness of geocoded address information"""
        required_fields = ['Street_Name', 'Postal_Code', 'City', 'Province_Name']
        present_count = 0
        
        for field in required_fields:
            value = row.get(field)
            if pd.notna(value) and str(value).strip() != '':
                present_count += 1
        
        completeness_score = present_count / len(required_fields)
        
        return {
            'completeness_score': completeness_score,
            'present_fields': present_count,
            'total_required': len(required_fields)
        }
    
    def classify_address_quality_enhanced(self, row):
        """
        Enhanced address quality classification with ULTRA_HIGH confidence level
        v2.9.8: Improved number matching and address completeness assessment
        """
        enhanced_config = self.config.get("enhanced_classification", {})
        ultra_high_threshold = enhanced_config.get("ultra_high_completeness_threshold", 0.75)
        high_threshold = enhanced_config.get("high_completeness_threshold", 0.5)
        enable_ultra_high = enhanced_config.get("enable_ultra_high_confidence", True)
        
        original = str(row.get('cleaned_ubicazione', '')).strip()
        geocoded = str(row.get('Geocoded_Address_Italian', '')).strip()
        has_geocoding = row.get('Geocoding_Status') == 'Success'
        
        # Use enhanced number extraction
        original_num = self.extract_street_number_enhanced(original)
        geocoded_num = self.extract_street_number_enhanced(geocoded) if has_geocoding else None
        
        # Handle SNC addresses
        if 'SNC' in original.upper():
            if has_geocoding and self.is_province_match(original, row.get('Province_Code')):
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Interpolation_Risk': False,
                    'Best_Address': original,
                    'Routing_Channel': 'AGENCY',
                    'Quality_Notes': 'SNC address - province match verified',
                    'Classification_Method': 'enhanced'
                }
            else:
                return {
                    'Address_Confidence': 'LOW',
                    'Interpolation_Risk': True,
                    'Best_Address': original,
                    'Routing_Channel': 'AGENCY',
                    'Quality_Notes': 'SNC address - geocoding failed or province mismatch',
                    'Classification_Method': 'enhanced'
                }
        
        # Enhanced number comparison
        if original_num and geocoded_num:
            similarity = self.calculate_number_similarity(original_num, geocoded_num)
            completeness = self.assess_address_completeness(row)
            
            # ULTRA_HIGH confidence - perfect match with complete data
            if (similarity['match_type'] == 'exact_match' and 
                completeness['completeness_score'] >= ultra_high_threshold and 
                enable_ultra_high):
                return {
                    'Address_Confidence': 'ULTRA_HIGH',
                    'Interpolation_Risk': False,
                    'Best_Address': geocoded,
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Perfect verification - {similarity["reason"]} (completeness: {completeness["completeness_score"]:.0%})',
                    'Classification_Method': 'enhanced'
                }
            
            # HIGH confidence - exact or base match with good data
            elif (similarity['match_type'] in ['exact_match', 'base_match'] and 
                  completeness['completeness_score'] >= high_threshold):
                return {
                    'Address_Confidence': 'HIGH',
                    'Interpolation_Risk': False,
                    'Best_Address': geocoded,
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Strong verification - {similarity["reason"]} (completeness: {completeness["completeness_score"]:.0%})',
                    'Classification_Method': 'enhanced'
                }
            
            # MEDIUM confidence - close numbers or lower completeness
            elif similarity['match_type'] in ['adjacent_number', 'close_number']:
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Interpolation_Risk': True,
                    'Best_Address': original,
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Close match - {similarity["reason"]} - using original for safety',
                    'Classification_Method': 'enhanced'
                }
            
            else:  # Different numbers
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Interpolation_Risk': True,
                    'Best_Address': original,
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Number verification - {similarity["reason"]} - using original',
                    'Classification_Method': 'enhanced'
                }
        
        # Original has number, geocoding failed to provide one
        elif original_num and not geocoded_num:
            # If original has a number and geocoding couldn't provide one,
            # but the original is still considered reliable for direct mail (e.g., Montichiari case)
            # We elevate its confidence to HIGH.
            return {
                'Address_Confidence': 'HIGH', # Elevated to HIGH
                'Interpolation_Risk': False,
                'Best_Address': original,
                'Routing_Channel': 'DIRECT_MAIL',
                'Quality_Notes': f'Original has number "{original_num}" and is considered deliverable despite geocoding not providing a number.',
                'Classification_Method': 'enhanced'
            }
        
        # No original number, geocoding suggested one
        elif not original_num and geocoded_num:
            return {
                'Address_Confidence': 'LOW',
                'Interpolation_Risk': True,
                'Best_Address': '',
                'Routing_Channel': 'AGENCY',
                'Quality_Notes': f'No original number, geocoding suggested "{geocoded_num}"',
                'Classification_Method': 'enhanced'
            }
        
        # No numbers anywhere
        else:
            return {
                'Address_Confidence': 'LOW',
                'Interpolation_Risk': False,
                'Best_Address': '',
                'Routing_Channel': 'AGENCY',
                'Quality_Notes': 'No street number available in any source',
                'Classification_Method': 'enhanced'
            }

    def classify_address_quality(self, row):
        """
        Classify address quality based on original vs geocoded comparison.
        v2.9.8: Now supports enhanced classification with configuration flag
        """
        # Check if enhanced classification is enabled
        enhanced_config = self.config.get("enhanced_classification", {})
        if enhanced_config.get("enabled", False):
            result = self.classify_address_quality_enhanced(row)
            self.logger.info(f"Enhanced classification: {row.get('cleaned_ubicazione', '')[:30]}... -> {result['Address_Confidence']}")
            return result
        
        # Original classification logic (unchanged for compatibility)
        original = str(row.get('cleaned_ubicazione', '')).strip()
        geocoded = str(row.get('Geocoded_Address_Italian', '')).strip()
        has_geocoding = row.get('Geocoding_Status') == 'Success'
        
        def extract_street_number(address):
            # Enhanced regex to capture numbers with suffixes like "32/A"
            patterns = [
                r'n\.?\s*(\d+[A-Za-z/]{0,2})',  # Handles "n. 32", "n. 32/A", "n.32B"
                r'\b(\d+[A-Za-z/]{0,2})$',      # Handles "32", "32/A" at the end of the string
                r',\s*(\d+[A-Za-z/]{0,2})'      # Handles ", 32", ", 32/A"
            ]
            for pattern in patterns:
                match = re.search(pattern, address, re.IGNORECASE)
                if match:
                    # Return the full matched group, converted to uppercase for consistent comparison
                    return match.group(1).upper()
            return None
        
        original_num = extract_street_number(original)
        geocoded_num = extract_street_number(geocoded) if has_geocoding else None
        
        # v2.9.2 REVISION: SNC addresses are now MEDIUM confidence and routed to AGENCY
        if 'SNC' in original.upper():
            # Province match check is still valuable to avoid major geocoding errors
            if has_geocoding and self.is_province_match(original, row.get('Province_Code')):
                return {
                    'Address_Confidence': 'MEDIUM', 
                    'Interpolation_Risk': False, 
                    'Best_Address': original, 
                    'Routing_Channel': 'AGENCY', 
                    'Quality_Notes': 'SNC address - province match verified',
                    'Classification_Method': 'original'
                }
            else:
                return {
                    'Address_Confidence': 'LOW', 
                    'Interpolation_Risk': True, 
                    'Best_Address': original, 
                    'Routing_Channel': 'AGENCY', 
                    'Quality_Notes': 'SNC address - geocoding failed or province mismatch',
                    'Classification_Method': 'original'
                }
        
        elif original_num and geocoded_num and original_num == geocoded_num:
            return {'Address_Confidence': 'HIGH', 'Interpolation_Risk': False, 'Best_Address': geocoded, 'Routing_Channel': 'DIRECT_MAIL', 'Quality_Notes': 'Complete and verified address', 'Classification_Method': 'original'}
        
        elif original_num and geocoded_num and original_num != geocoded_num:
            # If there's a number mismatch but the original address is still preferred and routed for DIRECT_MAIL,
            # we elevate its confidence to HIGH.
            if row.get('Best_Address') == original and row.get('Routing_Channel') == 'DIRECT_MAIL':
                return {
                    'Address_Confidence': 'HIGH', # Elevated to HIGH
                    'Interpolation_Risk': True, # Still has interpolation risk due to mismatch
                    'Best_Address': original,
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Number mismatch, but original preferred and routed for direct mail: {similarity["reason"]}',
                    'Classification_Method': 'enhanced'
                }
            else:
                # Otherwise, keep it as MEDIUM or LOW based on other factors
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Interpolation_Risk': True,
                    'Best_Address': original,
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Number mismatch. Using original number "{original_num}" instead of geocoded "{geocoded_num}"',
                    'Classification_Method': 'enhanced'
                }
        
        elif not original_num and geocoded_num:
            return {'Address_Confidence': 'LOW', 'Interpolation_Risk': True, 'Best_Address': '', 'Routing_Channel': 'AGENCY', 'Quality_Notes': 'Address has no number, geocoding API suggested one', 'Classification_Method': 'original'}
        
        elif original_num and not geocoded_num:
             return {'Address_Confidence': 'MEDIUM', 'Interpolation_Risk': False, 'Best_Address': original, 'Routing_Channel': 'DIRECT_MAIL', 'Quality_Notes': f'Original address has number "{original_num}", but it could not be verified by geocoding.', 'Classification_Method': 'original'}

        else: # No numbers in either source
            return {'Address_Confidence': 'LOW', 'Interpolation_Risk': False, 'Best_Address': '', 'Routing_Channel': 'AGENCY', 'Quality_Notes': 'No street number available in any source', 'Classification_Method': 'original'}
    
    def classify_owner_type(self, cf):
        """Classify owner type based on CF"""
        if pd.isna(cf) or not cf:
            return "Unknown"
        return "Azienda" if str(cf)[0].isdigit() else "Privato"

    def clean_addresses_safe(self, df):
        """Apply safe address cleaning logic without validation columns"""
        print("   🧹 Cleaning addresses...")
        def clean_single_address(address):
            if pd.isna(address): return ""
            address = str(address).strip()
            address = re.sub(r"\b(Piano|Scala|Appartamento|APT|Interno|Edificio|Lotto|Lotto\s*\w+)\b.*", "", address, flags=re.IGNORECASE).strip()
            # Normalize SNC to ensure consistent detection
            address = re.sub(r"n\.?\s*SNC", "n. SNC", address, flags=re.IGNORECASE)
            address = re.sub(r"(\d+)\s*-\s*(\d+)", r"\1-\2", address)
            return address
        
        if 'ubicazione' in df.columns:
            df['cleaned_ubicazione'] = df['ubicazione'].apply(clean_single_address)
        else:
            df['cleaned_ubicazione'] = ''
        
        return df

    def copy_to_onedrive(self, campaign_name, campaign_dir):
        """Copy results to OneDrive for team access"""
        onedrive_path = self.config.get("output_structure", {}).get("onedrive_sync_path")
        if not onedrive_path or not self.config.get("output_structure", {}).get("auto_copy_to_onedrive", False):
            return
        
        try:
            onedrive_campaign_dir = os.path.join(onedrive_path, campaign_name)
            if os.path.exists(onedrive_campaign_dir):
                shutil.rmtree(onedrive_campaign_dir)
            shutil.copytree(campaign_dir, onedrive_campaign_dir)
            print(f"   ✅ Results copied to OneDrive: {onedrive_campaign_dir}")
            self.create_team_notification_file(onedrive_campaign_dir, campaign_name)
        except Exception as e:
            print(f"   ❌ OneDrive sync failed: {str(e)}")

    def create_team_notification_file(self, onedrive_dir, campaign_name):
        """Create an updated, more effective email template for the team."""
        geocoding_summary = ""
        if self.geocoding_enabled:
            geocoding_summary = f"""
🗺️ ADDRESS ENHANCEMENT & QUALITY:
• Geocoding enabled: ZIP codes and coordinates added
• Addresses enhanced: {self.campaign_stats.get('addresses_geocoded', 0)}
• Success rate: {(self.campaign_stats.get('successful_geocodes', 0) / max(self.campaign_stats.get('addresses_geocoded', 1), 1)) * 100:.1f}%
• NEW: Address quality is now automatically classified to reduce returned mail.
  - 'Address_Confidence' column indicates reliability.
  - 'Routing_Channel' column suggests 'DIRECT_MAIL' or 'AGENCY'.
  - SNC addresses now routed to DIRECT_MAIL (postal service knows these streets)
"""
        pec_summary = ""
        if self.pec_enabled:
            pec_summary = f"""
- **Digital B2B Contacts (NEW!)**: For companies, certified PEC emails have been automatically retrieved to enable direct digital outreach.
"""

        notification_content = f"""
📧 **ACTION REQUIRED: Land Acquisition Campaign '{campaign_name}' Completed**

Hi Team,

The campaign "{campaign_name}" is complete. Results are in OneDrive and ready for your review.

---
**Key Improvements in this Output:**

- **Cleaner Contacts**: The `Validation_Ready.xlsx` file is now **de-duplicated**. You will only see each unique owner once per unique address, saving you time.
- **Smarter Addresses (v2.9!)**: Each address now has a quality score (`Address_Confidence`) and a recommended `Routing_Channel` (DIRECT_MAIL or AGENCY) to minimize costs from returned mail.
- **SNC Addresses Update**: SNC addresses are now sent to DIRECT_MAIL as postal service knows these small streets well.
{pec_summary}- **Smarter Summaries**: The `Municipality_Summary` sheet now contains powerful business intelligence metrics with complete funnel tracking.
- **Funnel Visibility**: New sheets show how many parcels and hectares flow through each processing stage.
---

**For the Land Acquisition Team:**

1.  **Primary File**: Go to the campaign folder and open `Validation_Ready.xlsx` in each municipality sub-folder.
2.  **Your Goal**: Identify high-quality prospects for our mailing campaigns.
3.  **Workflow**:
    * This list is now clean and efficient. 
    * **Focus on `Routing_Channel` = 'DIRECT_MAIL'**. These are the highest quality addresses.
    * Use `Address_Confidence` and `Quality_Notes` for more detail.
    * SNC addresses are now marked for DIRECT_MAIL (postal service change).
    {geocoding_summary}

**For the Business Development Team:**

- Please review the `Companies_Found.xlsx` files. They now include a `pec_email` column for direct digital contact with company owners.

**For Management:**

- The `PowerBI_Dataset.csv` has been updated with funnel metrics showing parcel/hectare flow through the process.
- The `Enhanced_Cost_Summary.txt` provides a full breakdown of campaign ROI and recovery savings.
- New `Funnel_Analysis` sheets in Excel files show complete process visibility.

**Location:**
`OneDrive > ... > Campaigns > {campaign_name}`

Any questions, please contact [Your Name].

Best,
[Your Name]
        """.strip()
        
        notification_file = os.path.join(onedrive_dir, "README_Team_Instructions.txt")
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(notification_content)

    def create_municipality_summary(self, municipality_key, municipality_data, df_raw, validation_ready, companies_found=None, funnel_metrics=None):
        """
        Creates an enhanced municipality summary with high-impact business metrics and funnel data.
        v2.9.2: Corrected summary logic for contacts and area; renamed/removed metrics.
        """
        # Standardize Area column before calculation
        if 'Area' in validation_ready.columns:
            validation_ready['Area'] = pd.to_numeric(validation_ready['Area'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

        if 'cf' not in df_raw.columns:
            return { "Error": "cf column not found in raw data" }
        df_raw['cf'] = df_raw['cf'].astype(str)

        individual_cfs = df_raw[
            (df_raw['cf'].str.len() > 0) & 
            (df_raw['cf'].str[0].str.isalpha())
        ]['cf'].unique()
        company_cfs = df_raw[
            (df_raw['cf'].str.len() > 0) & 
            (df_raw['cf'].str[0].str.isdigit())
        ]['cf'].unique()
        
        parcels_with_data = len(df_raw[['foglio_input', 'particella_input']].drop_duplicates())
        Property_Data_Retrieved_Rate = (parcels_with_data / municipality_data['parcel_count']) * 100 if municipality_data['parcel_count'] > 0 else 0
        
        individuals_cat_a_raw = df_raw[
            (df_raw['Tipo_Proprietario'] == 'Privato') & 
            (df_raw['Tipo_Proprietario'].notna()) & 
            (df_raw['classamento'].str.contains('Cat.A', na=False))
        ]
        Residential_Viability_Rate = (len(validation_ready) / len(individuals_cat_a_raw)) * 100 if len(individuals_cat_a_raw) > 0 else 0
        
        geocoding_success_count = 0
        if 'Geocoding_Status' in validation_ready.columns:
            geocoding_success_count = len(validation_ready[validation_ready['Geocoding_Status'] == 'Success'])
        Address_Verification_Rate = (geocoding_success_count / len(validation_ready)) * 100 if len(validation_ready) > 0 else 0

        # v2.9.2: Revised metric calculations
        direct_mail_contacts = 0
        agency_contacts = 0
        hectares_direct_mail = 0.0
        hectares_agency = 0.0
        interpolation_risks = 0

        if not validation_ready.empty and 'Address_Confidence' in validation_ready.columns:
            # REVISED v3.1.7: Direct Mail contacts now include ULTRA_HIGH, HIGH, and MEDIUM confidence addresses
            direct_mail_df = validation_ready[validation_ready['Address_Confidence'].isin(['ULTRA_HIGH', 'HIGH', 'MEDIUM'])]
            # REVISED v3.1.8: Agency contacts now count LOW confidence addresses for consistency
            agency_df = validation_ready[validation_ready['Address_Confidence'] == 'LOW']

            # Count addresses in each channel (v3.1.8: both metrics now count by confidence level)
            direct_mail_contacts = len(direct_mail_df)
            agency_contacts = len(agency_df)

            # Sum area of unique parcels in each channel
            hectares_direct_mail = direct_mail_df.drop_duplicates(subset=['foglio_input', 'particella_input'])['Area'].sum()
            hectares_agency = agency_df.drop_duplicates(subset=['foglio_input', 'particella_input'])['Area'].sum()

            interpolation_risks = len(validation_ready[validation_ready['Interpolation_Risk'] == True])

        companies_with_pec = 0
        pec_success_rate = 0.0
        if companies_found is not None and not companies_found.empty and 'pec_status' in companies_found.columns:
            companies_with_pec = len(companies_found[companies_found['pec_status'] == 'found'])
            total_companies_for_pec = len(companies_found)
            if total_companies_for_pec > 0:
                pec_success_rate = (companies_with_pec / total_companies_for_pec) * 100

        summary_dict = {
            # Traceability columns
            "CP": municipality_data['CP'],
            "comune": municipality_data['comune'],
            "provincia": municipality_data.get('provincia', ''),
            
            # Existing metrics
            "Input_Parcels": municipality_data['parcel_count'],
            "Property_Data_Retrieved_Rate": Property_Data_Retrieved_Rate,
            "Individual_Landowners_Found": len(individual_cfs),
            "Unique_Company_Owners": len(company_cfs),
            "Interpolation_Risks_Detected": interpolation_risks,
            "Hectares_Direct_Mail": hectares_direct_mail,
            "Companies_With_PEC": companies_with_pec,
            "Unique_Owners_on_Target_Parcels": validation_ready['cf'].nunique() if not validation_ready.empty else 0,
            "PEC_Success_Rate": pec_success_rate,
            "Residential_Viability_Rate": Residential_Viability_Rate,
            "Address_Verification_Rate": Address_Verification_Rate,
            
            # REVISED v2.9.2: Funnel Metrics
            "Input_Area_Ha": funnel_metrics.get("input_area_ha", 0) if funnel_metrics else 0,
            "After_API_Parcels": funnel_metrics.get("after_api_parcels", 0) if funnel_metrics else 0,
            "After_API_Area_Ha": funnel_metrics.get("after_api_area_ha", 0) if funnel_metrics else 0,
            "Private_Owner_Parcels": funnel_metrics.get("private_owner_parcels", 0) if funnel_metrics else 0,
            "Private_Owner_Area_Ha": funnel_metrics.get("private_owner_area_ha", 0) if funnel_metrics else 0,
            "Company_Owner_Parcels": funnel_metrics.get("company_owner_parcels", 0) if funnel_metrics else 0,
            "Company_Owner_Area_Ha": funnel_metrics.get("company_owner_area_ha", 0) if funnel_metrics else 0,
            "Residential_Contact_ParcelsResidential_Contact_Parcels": funnel_metrics.get("Residential_Contact_ParcelsResidential_Contact_Parcels", 0) if funnel_metrics else 0,
            "After_CatA_Filter_Area_Ha": funnel_metrics.get("after_cata_filter_area_ha", 0) if funnel_metrics else 0,
            "Unique_Owner_Address_Pairs": len(validation_ready) if not validation_ready.empty else 0, # FIXED
            "Direct_Mail_Final_Contacts": direct_mail_contacts, # REVISED
            "Direct_Mail_Final_Area_Ha": hectares_direct_mail, # REVISED
            "Agency_Final_Contacts": agency_contacts, # REVISED
            "Agency_Final_Area_Ha": hectares_agency, # REVISED
        }
        
        return summary_dict
    
    def setup_logging(self):
        """Setup centralized logging with Unicode support"""
        logs_dir = self.config.get("logs_directory", "logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_file = os.path.join(logs_dir, f'land_acquisition_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.info("Enhanced Land Acquisition Pipeline v2.9 initialized")
    
    def setup_directories(self):
        """Create necessary directories"""
        dirs_to_create = [self.config.get("output_structure", {}).get(key) for key in ["local_processing_dir", "completed_campaigns_dir"]] + ["cache", "logs"]
        for dir_name in dirs_to_create:
            if dir_name: os.makedirs(dir_name, exist_ok=True)
    
    def load_cache(self):
        """Load API cache"""
        cache_file = os.path.join(self.config.get("cache_directory", "cache"), "api_cache.pkl")
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                self.api_cache = pickle.load(f)
            self.logger.info(f"Loaded {len(self.api_cache)} cached API responses")
        else:
            self.api_cache = {}
    
    def save_cache(self):
        """Save API cache"""
        cache_file = os.path.join(self.config.get("cache_directory", "cache"), "api_cache.pkl")
        with open(cache_file, 'wb') as f:
            pickle.dump(self.api_cache, f)
    
    def init_campaign_stats(self):
        """Initialize campaign tracking with recovery and geocoding metrics"""
        return {
            "campaign_start": datetime.now(), "total_cps": 0, "total_municipalities": 0,
            "total_parcels": 0, "processed_parcels": 0, "successful_parcels": 0,
            "api_calls": 0, "api_cost": 0.0, "municipalities_processed": {}, "cp_summary": {},
            "validation_ready_count": 0, "powerbi_data": [], "start_balance": 0.0,
            "end_balance": 0.0, "campaign_cost": 0.0, "timeout_requests": 0,
            "recovery_attempts": 0, "successful_recoveries": 0, "recovery_cost_saved": 0.0,
            "pending_recovery_requests": [], "geocoding_enabled": False, "geocoding_api_calls": 0,
            "addresses_geocoded": 0, "successful_geocodes": 0, "addresses_with_rich_data": 0,
            "geocoding_timeout_requests": 0, "geocoding_recovery_attempts": 0,
            "successful_geocoding_recoveries": 0, "pec_enabled": False, "pec_api_calls": 0,
            "pec_found_count": 0
        }
    
    def analyze_input_structure(self, df):
        """Analyze the CP-Municipality structure of input data"""
        print("\n📊 ANALYZING INPUT STRUCTURE")
        has_sezione = 'Sezione' in df.columns and df['Sezione'].notna().sum() > 0
        cp_summary = df.groupby('CP').agg(
            comune=('comune', lambda x: list(x.unique())),
            provincia=('provincia', 'first'),
            parcel_count=('foglio', 'count')
        )
        
        self.campaign_stats.update({
            "total_cps": len(cp_summary), "total_municipalities": df['comune'].nunique(),
            "total_parcels": len(df), "geocoding_enabled": self.geocoding_enabled,
            "pec_enabled": self.pec_enabled
        })

        print(f"🎯 Connection Points (CP): {self.campaign_stats['total_cps']}")
        print(f"🏘️  Municipalities: {self.campaign_stats['total_municipalities']}")
        print(f"📍 Total Parcels: {self.campaign_stats['total_parcels']}")
        print(f"🗺️  Address Enhancement: {'✅ ENABLED' if self.geocoding_enabled else '❌ DISABLED'}")
        print(f"📧 PEC Email Integration: {'✅ ENABLED' if self.pec_enabled else '❌ DISABLED'}")
        print(f"📊 Funnel Tracking: ✅ ENABLED (v2.9)")
        
        print("\n📋 CP Structure:")
        for cp, row in cp_summary.iterrows():
            sezione_info = ""
            if has_sezione:
                unique_sezioni = df[df['CP'] == cp]['Sezione'].dropna().unique()
                if unique_sezioni.size > 0:
                    sezione_info = f" (Sezioni: {', '.join(map(str, unique_sezioni))})"
            print(f"   CP {cp} ({row['provincia']}): {row['parcel_count']} parcels across {', '.join(row['comune'])}{sezione_info}")
        
        self.campaign_stats["cp_summary"] = cp_summary.to_dict('index')
        return cp_summary
    
    def create_municipality_structure(self, df, campaign_name):
        """Create organized folder structure by municipality with short numeric IDs."""
        print(f"\n📁 CREATING MUNICIPALITY STRUCTURE (Optimized for Short Paths)")
        campaign_dir = os.path.join(self.config.get("output_structure", {}).get("completed_campaigns_dir", "completed_campaigns"), campaign_name)
        os.makedirs(campaign_dir, exist_ok=True)
        
        municipality_groups = df.groupby(['CP', 'comune'])
        municipality_structure = {}
        municipality_id_counter = 1
        
        for (cp, comune), group in municipality_groups:
            municipality_key = f"Mun_{municipality_id_counter:03d}"
            municipality_dir = os.path.join(campaign_dir, municipality_key)
            os.makedirs(municipality_dir, exist_ok=True)
            municipality_input = os.path.join(municipality_dir, f"{municipality_key}_input.xlsx")
            group.to_excel(municipality_input, index=False)
            
            municipality_structure[municipality_key] = {
                "CP": cp, "comune": comune, "provincia": group['provincia'].iloc[0],
                "parcel_count": len(group), "directory": municipality_dir,
                "input_file": municipality_input, "dataframe": group
            }
            print(f"   ✅ Folder '{municipality_key}' -> {cp}, {comune} ({len(group)} parcels)")
            municipality_id_counter += 1
        
        return municipality_structure
    
    def get_manual_balance_input(self, timing="start"):
        """Get manual balance input from user"""
        print(f"\n💰 COST TRACKING - {timing.upper()} BALANCE")
        print("Please check your API balance at https://catasto.openapi.it/dashboard")
        while True:
            try:
                balance = float(input("Enter your current balance (€): "))
                if timing == "start": self.campaign_stats["start_balance"] = balance
                else:
                    self.campaign_stats["end_balance"] = balance
                    self.campaign_stats["campaign_cost"] = self.campaign_stats["start_balance"] - balance
                return balance
            except ValueError:
                print("❌ Please enter a valid number (e.g., 45.50)")

    def get_cadastral_data(self, row, token):
        """Main function to get property owners from the catasto API with timeout recovery."""
        self.campaign_stats["api_calls"] += 1
        sezione_cache = str(row.get('Sezione', '')).strip() if 'Sezione' in row and pd.notna(row['Sezione']) else ''
        cache_key = f"cadastral_{row['tipo_catasto']}_{row['provincia']}_{row['comune']}_{row['foglio']}_{row['particella']}_{sezione_cache}"
        if cache_key in self.api_cache:
            return self.api_cache[cache_key]

        url = "https://catasto.openapi.it/richiesta/prospetto_catastale"
        headers = {"content-type": "application/json", "Authorization": f"Bearer {token}"}
        
        payload = {"tipo_catasto": row['tipo_catasto'], "provincia": row['provincia'], "comune": row['comune'], "foglio": int(row['foglio']), "particella": int(row['particella'])}

        if 'Sezione' in row and pd.notna(row['Sezione']) and str(row['Sezione']).strip():
            payload["sezione"] = str(row['Sezione']).strip()
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                return [{"denominazione": f"Error_{response.status_code}", "cf": f"Error_{response.status_code}", "persona_data": None}]
            request_id = response.json()['data']['id']
            timeout_key = f"timeout_request_{request_id}"
            self.api_cache[timeout_key] = {"request_id": request_id, "params": payload, "timestamp": datetime.now().isoformat(), "cache_key": cache_key, "status": "pending"}
            self.save_cache()
            
            status_url = f"https://catasto.openapi.it/richiesta/{request_id}"
            for attempt in range(60):
                print(f"  [Cadastral API] Attempt {attempt+1}/60 for Foglio={row['foglio']}, Particella={row['particella']}", end='\r')
                status_response = requests.get(status_url, headers=headers)
                if status_response.status_code == 200:
                    response_data = status_response.json()
                    if (response_data.get('data', {}).get('risultato') and response_data['data']['risultato'].get('immobili')):
                        immobile = response_data['data']['risultato']['immobili'][0]
                        all_owners_data = []
                        for intestatario in immobile.get('intestatari', []):
                            cf = intestatario.get('cf', 'N/A')
                            persona_data = {}
                            if cf != 'N/A' and not self.is_company_cf(cf):
                                persona_result = self.get_persona_data(cf, row, token)
                                if persona_result.get('persona_data'):
                                    persona_data = persona_result['persona_data']
                            all_owners_data.append({"denominazione": intestatario.get('denominazione', 'N/A'), "cf": cf, "quota": intestatario.get('quota', 'N/A'), "persona_data": persona_data})
                        self.api_cache.pop(timeout_key, None)
                        self.api_cache[cache_key] = all_owners_data
                        self.save_cache()
                        return all_owners_data
                    if response_data.get('data', {}).get('stato') in ['evasa', 'completato']:
                        break
                time.sleep(3)
            
            self.api_cache[timeout_key]["status"] = "timeout"
            self.save_cache()
            self.campaign_stats["timeout_requests"] += 1
            return [{"denominazione": "Timeout", "cf": "Timeout", "persona_data": None, "request_id": request_id}]
        except Exception as e:
            return [{"denominazione": f"Error: {str(e)[:50]}", "cf": "Error", "persona_data": None}]

    def recover_timeout_requests(self, token):
        """
        Attempt to recover data from timed-out API requests
        """
        if not self.config.get("timeout_recovery", {}).get("enable_recovery", True):
            return
        print(f"\n🔄 TIMEOUT RECOVERY SYSTEM")
        timeout_entries = {k: v for k, v in self.api_cache.items() if k.startswith("timeout_request_") and v.get("status") in ["pending", "timeout"]}
        if not timeout_entries:
            print("   ✅ No timeout requests found.")
            return
        
        recovered_count = 0
        for timeout_key, recovery_data in timeout_entries.items():
            request_id = recovery_data["request_id"]
            print(f"   🔄 Checking {request_id[:8]}... ", end="")
            status_url = f"https://catasto.openapi.it/richiesta/{request_id}"
            headers = {"content-type": "application/json", "Authorization": f"Bearer {token}"}
            try:
                status_response = requests.get(status_url, headers=headers)
                if status_response.status_code == 200:
                    response_data = status_response.json()
                    if (response_data.get('data', {}).get('risultato') and response_data['data']['risultato'].get('immobili')):
                        immobile = response_data['data']['risultato']['immobili'][0]
                        intestatari = immobile.get('intestatari', []) or []
                        all_owners_data = [{"denominazione": i.get('denominazione', 'N/A'), "cf": i.get('cf', 'N/A'), "quota": i.get('quota', 'N/A'), "persona_data": None, "recovered": True} for i in intestatari]
                        self.api_cache[recovery_data["cache_key"]] = all_owners_data
                        self.api_cache.pop(timeout_key, None)
                        recovered_count += 1
                        print(f"✅ RECOVERED! ({len(all_owners_data)} owners)")
                    elif response_data.get('data', {}).get('stato') in ['evasa', 'completato']:
                        self.api_cache[recovery_data["cache_key"]] = [{"denominazione": "No Data", "cf": "No Data", "persona_data": None}]
                        self.api_cache.pop(timeout_key, None)
                        print(f"✅ No data available")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        self.save_cache()
        if recovered_count > 0:
            print(f"   🎉 RECOVERY SUMMARY: Successfully recovered {recovered_count} requests.")

    def is_company_cf(self, cf):
        """Check if the CF is for a company (starts with a digit)."""
        return cf and str(cf)[0].isdigit()

    def get_persona_data(self, cf, row, token):
        """Call the catasto API to retrieve personal data about a specific CF."""
        self.campaign_stats["api_calls"] += 1
        cache_key = f"persona_{cf}_{row['provincia']}"
        if cache_key in self.api_cache:
            return self.api_cache[cache_key]

        url = "https://catasto.openapi.it/richiesta/ricerca_persona"
        headers = {"content-type": "application/json", "Authorization": f"Bearer {token}"}
        payload = {"cf_piva": cf, "tipo_catasto": "F", "provincia": row['provincia']}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200: return {"persona_data": None}
            request_id = response.json()['data']['id']
            status_url = f"https://catasto.openapi.it/richiesta/{request_id}"
            for attempt in range(60):
                status_response = requests.get(status_url, headers=headers)
                if status_response.status_code == 200:
                    response_data = status_response.json()
                    if response_data.get('data', {}).get('risultato'):
                        result = {"persona_data": response_data['data']['risultato']}
                        self.api_cache[cache_key] = result
                        self.save_cache()
                        return result
                    if response_data.get('data', {}).get('stato') in ['evasa', 'completato']:
                        break
                time.sleep(3)
            return {"persona_data": None}
        except Exception:
            return {"persona_data": None}

    def process_persona_data(self, row_index, persona_data_str, original_row, quota=''):
        """Convert the persona_data JSON into row(s) linking one owner to one or more properties."""
        try:
            data = json.loads(persona_data_str) if isinstance(persona_data_str, str) else persona_data_str
            if not data or not isinstance(data, dict) or not data.get('soggetti'): return []
            soggetto = data['soggetti'][0]
            personal_info = {'cognome': soggetto.get('cognome', ''), 'nome': soggetto.get('nome', ''), 'data_nascita': soggetto.get('data_nascita', ''), 'luogo_nascita': soggetto.get('luogo_nascita', ''), 'sesso': soggetto.get('sesso', ''), 'cf': soggetto.get('cf', ''), 'quota': quota, 'immobili_count': len(soggetto.get('immobili', []))}
            base_row = {'tipo_catasto': original_row.get('tipo_catasto', ''), 'CP': original_row.get('CP', ''), 'provincia_input': original_row.get('provincia', ''), 'comune_input': original_row.get('comune', ''), 'foglio_input': original_row.get('foglio', ''), 'particella_input': original_row.get('particella', ''), 'Area': original_row.get('Area', ''), 'Sezione': original_row.get('Sezione', ''), 'denominazione': original_row.get('denominazione', '')}
            rows_to_add = []
            if not soggetto.get('immobili'):
                google_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(original_row.get('ubicazione', ''))}"
                rows_to_add.append({**base_row, **personal_info, 'Maps_link': google_link, 'ubicazione': original_row.get('ubicazione', ''), 'classamento': ''})
            else:
                for immobile in soggetto.get('immobili', []):
                    ubic = immobile.get('ubicazione', '')
                    google_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(ubic)}"
                    rows_to_add.append({**base_row, **personal_info, 'ubicazione': ubic, 'Maps_link': google_link, 'catasto': immobile.get('catasto', ''), 'titolarita': immobile.get('titolarita', ''), 'provincia': immobile.get('provincia', ''), 'comune': immobile.get('comune', ''), 'codice_catastale': immobile.get('codice_catastale', ''), 'foglio': immobile.get('foglio', ''), 'particella': immobile.get('particella', ''), 'classamento': immobile.get('classamento', '')})
            return rows_to_add
        except Exception:
            return []

    def run_complete_campaign(self, input_file, campaign_name, start_balance=None):
        """v2.9.5: Main method to run the campaign, now aggregates all results into a single file."""
        print(f"\n🚀 ENHANCED LAND ACQUISITION CAMPAIGN v2.9.5: {campaign_name}")
        if start_balance is None:
            start_balance = self.get_manual_balance_input("start")
        else:
            self.campaign_stats["start_balance"] = start_balance
        
        try:
            df = pd.read_excel(input_file, dtype={'Area': str})
        except Exception as e:
            print(f"❌ Failed to load input file: {e}"); return None
        
        self.analyze_input_structure(df)
        municipality_groups = df.groupby(['CP', 'comune'])
        token = self.config.get("api_settings", {}).get("token", "")
        if not token or token == "YOUR_TOKEN_HERE":
            print("❌ Please update your API token in land_acquisition_config.json"); return None
        
        # v2.9.5: Lists to hold results from all municipalities
        all_raw_data = []
        all_validation_ready = []
        all_companies_found = []
        all_summaries = []
        all_funnels = []

        for (cp, comune), group in municipality_groups:
            municipality_key = f"{cp}_{comune.replace(' ', '_')}" # Use a descriptive key
            municipality_data = {"CP": cp, "comune": comune, "parcel_count": len(group), "dataframe": group}
            
            # Process data in memory
            processed_results = self.process_municipality(municipality_key, municipality_data, token)
            
            if processed_results:
                # Append results to the master lists
                all_raw_data.append(processed_results['raw_data'])
                all_validation_ready.append(processed_results['validation_ready'])
                all_companies_found.append(processed_results['companies_found'])
                all_summaries.append(processed_results['summary'])
                all_funnels.append(processed_results['funnel'])

            self.save_cache()
            if self.geocoding_enabled: self.save_geocoding_cache()
            if self.pec_enabled: self.save_pec_cache()

        if self.campaign_stats["timeout_requests"] > 0:
            self.recover_timeout_requests(token)
        if self.geocoding_enabled and self.campaign_stats["geocoding_timeout_requests"] > 0:
            self.recover_geocoding_timeout_requests()
        
        # v2.9.5: Create the single, consolidated output file
        self.create_consolidated_excel_output(campaign_name, all_raw_data, all_validation_ready, all_companies_found, all_summaries, all_funnels)

        self.get_manual_balance_input("end")
        campaign_dir = os.path.join(self.config.get("output_structure", {}).get("completed_campaigns_dir", "completed_campaigns"), campaign_name)
        self.create_enhanced_cost_summary(campaign_name, campaign_dir)
        # PowerBI export for dashboard integration
        print("🔍 DEBUG: Starting PowerBI export...")
        try:
            self.create_powerbi_export_from_consolidated_data(campaign_name, campaign_dir)
            print("✅ PowerBI export function completed")
        except Exception as e:
            print(f"❌ PowerBI export failed: {str(e)}")
            import traceback
            traceback.print_exc()
        self.copy_to_onedrive(campaign_name, campaign_dir)
        
        print(f"\n✅ ENHANCED CAMPAIGN COMPLETED (v2.9.5)")

    def create_enhanced_cost_summary(self, campaign_name, campaign_dir):
        """Create enhanced cost summary."""
        geocoding_section = f"Geocoding Enabled: {'Yes' if self.geocoding_enabled else 'No'}\n"
        pec_section = f"PEC Integration Enabled: {'Yes' if self.pec_enabled else 'No'}\n"

        cost_summary = f"""
ENHANCED LAND ACQUISITION CAMPAIGN COST SUMMARY v2.9
Campaign: {campaign_name}
Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

💰 COST BREAKDOWN:
Start Balance: €{self.campaign_stats['start_balance']:.2f}
End Balance: €{self.campaign_stats['end_balance']:.2f}
Total Campaign Cost: €{self.campaign_stats['campaign_cost']:.2f}

{geocoding_section}{pec_section}
Funnel Tracking: Enabled (v2.9)
SNC Routing: Direct Mail (v2.9)

📊 PROCESSING STATS:
Total API Calls: {self.campaign_stats['api_calls']}
Total Parcels: {self.campaign_stats['total_parcels']}
Processed Parcels: {self.campaign_stats['processed_parcels']}
Validation Ready Records: {self.campaign_stats['validation_ready_count']}
        """.strip()
        
        cost_file = os.path.join(campaign_dir, "Enhanced_Cost_Summary.txt")
        with open(cost_file, 'w', encoding='utf-8') as f:
            f.write(cost_summary)

    def process_municipality(self, municipality_key, municipality_data, token):
        """Process a single municipality through the complete pipeline with funnel tracking"""
        print(f"\n🏘️  PROCESSING: {municipality_key} | CP: {municipality_data['CP']} | Parcels: {municipality_data['parcel_count']}")
        df = municipality_data['dataframe']
        
        # v2.9: Initialize funnel tracking
        funnel_metrics = {
            "input_parcels": len(df),
            "input_area_ha": pd.to_numeric(df['Area'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).sum(),
            "after_api_parcels": 0,
            "after_api_area_ha": 0.0,
            "private_owner_parcels": 0,
            "private_owner_area_ha": 0.0,
            "company_owner_parcels": 0,
            "company_owner_area_ha": 0.0,
            "Residential_Contact_ParcelsResidential_Contact_Parcels": 0,
            "after_cata_filter_area_ha": 0.0,
            "unique_contacts": 0,
            "direct_mail_contacts": 0,
            "direct_mail_area_ha": 0.0,
            "agency_contacts": 0,
            "agency_area_ha": 0.0
        }
        
        raw_results = []
        try:
            for index, row in df.iterrows():
                results = self.get_cadastral_data(row, token)
                if results and not all(r['denominazione'] in ['Timeout', 'No Data'] or 'Error' in r['denominazione'] for r in results):
                    # v2.9: Track successful API calls
                    funnel_metrics["after_api_parcels"] += 1
                    funnel_metrics["after_api_area_ha"] += pd.to_numeric(str(row.get('Area', 0)).replace(',', '.'), errors='coerce') or 0
                    
                    for result in results:
                        if result['persona_data']:
                            processed_rows = self.process_persona_data(index, result['persona_data'], row, result.get('quota',''))
                            raw_results.extend(processed_rows)
                        else:
                            raw_results.append(self.create_base_row(row, result))
                self.campaign_stats["processed_parcels"] += 1
                print(f"   Progress: {(self.campaign_stats['processed_parcels']/self.campaign_stats['total_parcels'])*100:.1f}%", end='\r')
                time.sleep(self.config.get("api_settings", {}).get("sleep_between_calls", 2))
        except Exception as e:
            print(f"❌ Error during municipality processing: {e}")
            self.logger.error(f"Error processing {municipality_key}: {e}")
            return None
        
        print(f"\n   ✅ Completed: {len(df)}/{len(df)} parcels processed")
        if not raw_results:
            print(f"   ⚠️  No results for {municipality_key}"); return None
            
        # Pass funnel_metrics to output creation
        return self.create_municipality_output(municipality_key, municipality_data, raw_results, funnel_metrics)

    def create_base_row(self, row, owner_data):
        """Create base row for owner data, ensuring schema consistency."""
        base = {
            'tipo_catasto': row.get('tipo_catasto', ''), 'CP': row.get('CP', ''),
            'provincia_input': row.get('provincia', ''), 'comune_input': row.get('comune', ''),
            'foglio_input': row.get('foglio', ''), 'particella_input': row.get('particella', ''),
            'Area': row.get('Area', ''), 'Sezione': row.get('Sezione', ''),
            'denominazione': owner_data.get('denominazione', ''), 'cf': owner_data.get('cf', ''),
            'quota': owner_data.get('quota', ''),
            'cognome': owner_data.get('denominazione', '') if self.is_company_cf(owner_data.get('cf', '')) else '',
            'nome': '', 'data_nascita': '', 'luogo_nascita': '', 'sesso': '',
            'immobili_count': 0, 'catasto': '', 'titolarita': '', 'ubicazione': '',
            'Maps_link': '', 'provincia': row.get('provincia', ''), 'comune': row.get('comune', ''),
            'codice_catastale': '', 'foglio': row.get('foglio', ''), 'particella': row.get('particella', ''),
            'classamento': '', 'cadastral_reference': ''
        }
        return base

    def create_municipality_output(self, municipality_key, municipality_data, raw_results, funnel_metrics):
        """v2.9.9: Processes data for a single municipality and returns a dictionary of DataFrames."""
        df_raw = pd.DataFrame(raw_results)
        if df_raw.empty:
            self.logger.warning(f"No raw results for {municipality_key}")
            return None

        # FIX: Standardize column names for consistency before any processing
        # This resolves the KeyError for 'cf' and 'Area' by ensuring all rows have the same column structure.
        df_raw.rename(columns={
            'cf': 'cf_owner', 'denominazione': 'denominazione_owner',
            'tipo_soggetto': 'tipo_soggetto_owner', 'codice_diritto': 'codice_diritto_owner',
            'descrizione_diritto': 'descrizione_diritto_owner', 'quota': 'quota_owner',
            'comune_sede': 'comune_sede_owner', 'provincia_sede': 'provincia_sede_owner',
            'Area': 'Area_input', 'Sezione': 'sezione_input'
        }, inplace=True, errors='ignore')

        df_raw['CP'] = municipality_data['CP']
        df_raw['comune'] = municipality_data['comune']
        df_raw['Tipo_Proprietario'] = df_raw['cf_owner'].apply(self.classify_owner_type)

        # --- Funnel Tracking ---
        if 'Tipo_Proprietario' in df_raw.columns:
            private_mask = (df_raw['Tipo_Proprietario'] == 'Privato') & (df_raw['Tipo_Proprietario'].notna())
            company_mask = (df_raw['Tipo_Proprietario'] == 'Azienda') & (df_raw['Tipo_Proprietario'].notna())
            private_parcels = df_raw[private_mask][['foglio_input', 'particella_input']].drop_duplicates()
            company_parcels = df_raw[company_mask][['foglio_input', 'particella_input']].drop_duplicates()
            funnel_metrics["private_owner_parcels"] = len(private_parcels)
            funnel_metrics["company_owner_parcels"] = len(company_parcels)

            private_area_df = df_raw[private_mask].drop_duplicates(subset=['foglio_input', 'particella_input'])
            funnel_metrics["private_owner_area_ha"] = pd.to_numeric(private_area_df['Area_input'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).sum()
            
            company_area_df = df_raw[company_mask].drop_duplicates(subset=['foglio_input', 'particella_input'])
            funnel_metrics["company_owner_area_ha"] = pd.to_numeric(company_area_df['Area_input'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).sum()

        individuals_cat_a = df_raw[(df_raw['Tipo_Proprietario'] == 'Privato') & (df_raw['classamento'].str.contains('Cat.A', na=False, case=False))]
        companies_found = df_raw[(df_raw['Tipo_Proprietario'] == 'Azienda')].copy()
        
        if not individuals_cat_a.empty:
            cat_a_parcels = individuals_cat_a[['foglio_input', 'particella_input']].drop_duplicates()
            funnel_metrics["Residential_Contact_ParcelsResidential_Contact_Parcels"] = len(cat_a_parcels)
            cat_a_area_df = individuals_cat_a.drop_duplicates(subset=['foglio_input', 'particella_input'])
            funnel_metrics["after_cata_filter_area_ha"] = pd.to_numeric(cat_a_area_df['Area_input'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).sum()

        validation_ready = pd.DataFrame()
        if not individuals_cat_a.empty:
            validation_ready = individuals_cat_a.copy()
            validation_ready = self.clean_addresses_safe(validation_ready)
            if self.geocoding_enabled:
                validation_ready = self.enhance_addresses_with_geocoding(validation_ready)
                classification_results = validation_ready.apply(self.classify_address_quality, axis=1).apply(pd.Series)
                validation_ready = pd.concat([validation_ready, classification_results], axis=1)
            validation_ready.drop_duplicates(subset=['cf_owner', 'cleaned_ubicazione', 'foglio_input', 'particella_input'], inplace=True)

        if self.pec_enabled and not companies_found.empty:
            print(f"   📧 Enhancing {len(companies_found)} company records with PEC emails...")
            pec_results = companies_found['cf_owner'].apply(self.get_company_pec)
            companies_found[['pec_email', 'pec_status']] = pec_results.apply(pd.Series)
            time.sleep(self.pec_sleep)

        summary_data = self.create_municipality_summary(municipality_key, municipality_data, df_raw, validation_ready, companies_found, funnel_metrics)
        funnel_df = self.create_funnel_analysis_df(summary_data, funnel_metrics, municipality_data)
        print(f"   📊 Funnel Analysis: {funnel_metrics['input_parcels']} parcels → {summary_data.get('Unique_Owner_Address_Pairs', 0)} contacts")
        
        return {"raw_data": df_raw, "validation_ready": validation_ready, "companies_found": companies_found, "summary": summary_data, "funnel": funnel_df}


    def create_funnel_analysis_df(self, summary_metrics, funnel_metrics, municipality_data):
        """v3.1.1: Creates enhanced dual funnel analysis with business-friendly labels and metrics."""
        provincia = municipality_data.get('provincia', '')
        cp = municipality_data.get('CP', '')
        comune = municipality_data.get('comune', '')

        # LAND ACQUISITION PIPELINE
        land_acquisition_data = [
            {'Funnel_Type': 'Land Acquisition','Stage': '1. Input Parcels','Count': funnel_metrics.get('input_parcels', 0),'Hectares': round(funnel_metrics.get('input_area_ha', 0), 1),'Conversion / Multiplier': None,'Retention_Rate': 100.0,'Business_Rule': 'Parcels selected by Land Acquisition team.','Automation_Level': 'Manual','Process_Notes': 'Starting point of the campaign.','CP': cp, 'comune': comune, 'provincia': provincia},
            {'Funnel_Type': 'Land Acquisition','Stage': '2. Ownership Data Retrieved','Count': funnel_metrics.get('after_api_parcels', 0),'Hectares': round(funnel_metrics.get('after_api_area_ha', 0), 1),'Conversion / Multiplier': round((funnel_metrics.get('after_api_parcels', 0) / funnel_metrics.get('input_parcels', 1) * 100), 1) if funnel_metrics.get('input_parcels', 0) > 0 else 0,'Retention_Rate': round((funnel_metrics.get('after_api_parcels', 0) / funnel_metrics.get('input_parcels', 1) * 100), 1) if funnel_metrics.get('input_parcels', 0) > 0 else 0,'Business_Rule': 'System retrieves ownership from API.','Automation_Level': 'Fully-Auto','Process_Notes': f"API success rate.",'CP': cp, 'comune': comune, 'provincia': provincia},
            {'Funnel_Type': 'Land Acquisition','Stage': '3. Parcels w/ Private Owners','Count': summary_metrics.get('Private_Owner_Parcels', 0),'Hectares': round(summary_metrics.get('Private_Owner_Area_Ha', 0), 1),'Conversion / Multiplier': round((summary_metrics.get('Private_Owner_Parcels', 0) / funnel_metrics.get('after_api_parcels', 1) * 100), 1) if funnel_metrics.get('after_api_parcels', 0) > 0 else 0,'Retention_Rate': round((summary_metrics.get('Private_Owner_Parcels', 0) / funnel_metrics.get('input_parcels', 1) * 100), 1) if funnel_metrics.get('input_parcels', 0) > 0 else 0,'Business_Rule': 'Filters for individual owners.','Automation_Level': 'Fully-Auto','Process_Notes': 'Primary campaign target.','CP': cp, 'comune': comune, 'provincia': provincia},
            {'Funnel_Type': 'Land Acquisition','Stage': '4. Parcels w/ Residential Buildings','Count': summary_metrics.get('Residential_Contact_ParcelsResidential_Contact_Parcels', 0),'Hectares': round(summary_metrics.get('After_CatA_Filter_Area_Ha', 0), 1),'Conversion / Multiplier': round((summary_metrics.get('Residential_Contact_ParcelsResidential_Contact_Parcels', 0) / summary_metrics.get('Private_Owner_Parcels', 1) * 100), 1) if summary_metrics.get('Private_Owner_Parcels', 0) > 0 else 0,'Retention_Rate': round((summary_metrics.get('Residential_Contact_ParcelsResidential_Contact_Parcels', 0) / funnel_metrics.get('input_parcels', 1) * 100), 1) if funnel_metrics.get('input_parcels', 0) > 0 else 0,'Business_Rule': 'Filters for Catasto Category A.','Automation_Level': 'Fully-Auto','Process_Notes': 'Parcels likely to have a valid residential address.','CP': cp, 'comune': comune, 'provincia': provincia}
        ]
        
        # CONTACT PROCESSING PIPELINE
        owner_discovery_count_for_retention = summary_metrics.get('Unique_Owners_on_Target_Parcels', 0)
        contact_processing_data = [
            {'Funnel_Type': 'Contact Processing','Stage': '1. Owner Discovery','Count': owner_discovery_count_for_retention,'Hectares': round(summary_metrics.get('After_CatA_Filter_Area_Ha', 0), 1),'Conversion / Multiplier': round(owner_discovery_count_for_retention / (summary_metrics.get('Residential_Contact_ParcelsResidential_Contact_Parcels') if summary_metrics.get('Residential_Contact_ParcelsResidential_Contact_Parcels') else 1), 2),'Retention_Rate': 100.0,'Stage_Conversion_Rate': 100.0,'Business_Rule': 'Multiple owners can be identified for a single parcel.','Automation_Level': 'Fully-Auto','Process_Notes': 'Average # of unique owners per qualified parcel.','CP': cp, 'comune': comune, 'provincia': provincia},
            {'Funnel_Type': 'Contact Processing','Stage': '2. Address Expansion','Count': summary_metrics.get('Unique_Owner_Address_Pairs', 0),'Hectares': round(summary_metrics.get('After_CatA_Filter_Area_Ha', 0), 1),'Conversion / Multiplier': round(summary_metrics.get('Unique_Owner_Address_Pairs', 0) / (owner_discovery_count_for_retention if owner_discovery_count_for_retention else 1), 2),'Retention_Rate': round((summary_metrics.get('Unique_Owner_Address_Pairs', 0) / (owner_discovery_count_for_retention if owner_discovery_count_for_retention else 1) * 100), 1),'Stage_Conversion_Rate': round((summary_metrics.get('Unique_Owner_Address_Pairs', 0) / (owner_discovery_count_for_retention if owner_discovery_count_for_retention else 1) * 100), 1),'Business_Rule': 'All known residential addresses are collected for each unique owner.','Automation_Level': 'Fully-Auto','Process_Notes': 'Average # of addresses found per owner.','CP': cp, 'comune': comune, 'provincia': provincia},
            {'Funnel_Type': 'Contact Processing','Stage': '3. Address Validation & Enhancement','Count': summary_metrics.get('Unique_Owner_Address_Pairs', 0),'Hectares': round(summary_metrics.get('After_CatA_Filter_Area_Ha', 0), 1),'Conversion / Multiplier': None,'Retention_Rate': round((summary_metrics.get('Unique_Owner_Address_Pairs', 0) / (owner_discovery_count_for_retention if owner_discovery_count_for_retention else 1) * 100), 1),'Stage_Conversion_Rate': 100.0,'Business_Rule': 'All addresses are processed through geocoding and quality assessment.','Automation_Level': 'Fully-Auto','Process_Notes': 'This is a data enrichment step; all addresses are retained and classified.','CP': cp, 'comune': comune, 'provincia': provincia},
            {'Funnel_Type': 'Contact Processing','Stage': '4. Direct Mail Ready','Count': summary_metrics.get('Direct_Mail_Final_Contacts', 0),'Hectares': round(summary_metrics.get('Direct_Mail_Final_Area_Ha', 0), 1),'Conversion / Multiplier': round((summary_metrics.get('Direct_Mail_Final_Contacts', 0) / (owner_discovery_count_for_retention if owner_discovery_count_for_retention else 1)), 2),'Retention_Rate': round((summary_metrics.get('Direct_Mail_Final_Contacts', 0) / (owner_discovery_count_for_retention if owner_discovery_count_for_retention else 1) * 100), 1),'Stage_Conversion_Rate': round((summary_metrics.get('Direct_Mail_Final_Contacts', 0) / (summary_metrics.get('Unique_Owner_Address_Pairs') if summary_metrics.get('Unique_Owner_Address_Pairs') else 1) * 100), 1),'Business_Rule': 'High-confidence addresses are routed for direct mailing.','Automation_Level': 'Semi-Auto','Process_Notes': 'Contacts reliable enough for immediate outreach.','CP': cp, 'comune': comune, 'provincia': provincia},
            {'Funnel_Type': 'Contact Processing','Stage': '5. Agency Investigation Required','Count': summary_metrics.get('Agency_Final_Contacts', 0),'Hectares': round(summary_metrics.get('Agency_Final_Area_Ha', 0), 1),'Conversion / Multiplier': round((summary_metrics.get('Agency_Final_Contacts', 0) / (owner_discovery_count_for_retention if owner_discovery_count_for_retention else 1)), 2),'Retention_Rate': round((summary_metrics.get('Agency_Final_Contacts', 0) / (owner_discovery_count_for_retention if owner_discovery_count_for_retention else 1) * 100), 1),'Stage_Conversion_Rate': round((summary_metrics.get('Agency_Final_Contacts', 0) / (summary_metrics.get('Unique_Owner_Address_Pairs') if summary_metrics.get('Unique_Owner_Address_Pairs') else 1) * 100), 1),'Business_Rule': 'Low-confidence addresses require external agency investigation.','Automation_Level': 'Manual','Process_Notes': 'Contacts require manual verification.','CP': cp, 'comune': comune, 'provincia': provincia}
        ]
        df = pd.DataFrame(land_acquisition_data + contact_processing_data)
        df.rename(columns={'Conversion_Rate': 'Conversion / Multiplier'}, inplace=True)
        return df

    def create_quality_distribution_df(self, df_validation, campaign_cp, campaign_municipalities, campaign_provincia):
        """v3.1.1: Create address quality distribution with corrected rounding logic."""
        if df_validation.empty: return pd.DataFrame()
        quality_counts = df_validation['Address_Confidence'].value_counts()
        total_addresses = len(df_validation)
        quality_definitions = {
            'ULTRA_HIGH': {'Processing_Type': 'Zero Touch', 'Business_Value': 'Immediate print ready', 'Automation_Level': 'Fully-Auto', 'Routing_Decision': 'Direct Mail'},
            'HIGH': {'Processing_Type': 'Quick Review', 'Business_Value': 'Minimal validation needed', 'Automation_Level': 'Semi-Auto', 'Routing_Decision': 'Direct Mail'},
            'MEDIUM': {'Processing_Type': 'Standard Review', 'Business_Value': 'Normal processing required', 'Automation_Level': 'Manual', 'Routing_Decision': 'Mixed (Direct Mail + Agency)'},
            'LOW': {'Processing_Type': 'Agency Routing', 'Business_Value': 'External investigation required', 'Automation_Level': 'Manual', 'Routing_Decision': 'Agency'}
        }
        quality_levels = ['ULTRA_HIGH', 'HIGH', 'MEDIUM', 'LOW']
        quality_data = []
        percentages = []
        if total_addresses > 0:
            raw_percentages = [(quality_counts.get(level, 0) / total_addresses) * 100 for level in quality_levels]
            for i in range(len(raw_percentages) - 1):
                percentages.append(round(raw_percentages[i], 1))
            last_percentage = 100.0 - sum(percentages)
            percentages.append(round(last_percentage, 1))
        else:
            percentages = [0.0, 0.0, 0.0, 0.0]
        for i, quality_level in enumerate(quality_levels):
            count = quality_counts.get(quality_level, 0)
            quality_info = quality_definitions.get(quality_level, {})
            quality_data.append({
                'Quality_Level': quality_level, 'Count': count, 'Percentage': percentages[i],
                'Processing_Type': quality_info.get('Processing_Type', 'Unknown'),
                'Business_Value': quality_info.get('Business_Value', 'Not defined'),
                'Automation_Level': quality_info.get('Automation_Level', 'Manual'),
                'Routing_Decision': quality_info.get('Routing_Decision', 'Unknown'),
                'CP': campaign_cp,
                'comune': '; '.join(campaign_municipalities) if isinstance(campaign_municipalities, list) else campaign_municipalities,
                'provincia': campaign_provincia
            })
        return pd.DataFrame(quality_data)

    def create_quality_distribution_df(self, df_validation, campaign_cp, campaign_municipalities, campaign_provincia):
        """v3.1.1: Create address quality distribution with corrected rounding logic."""
        if df_validation.empty: return pd.DataFrame()
        quality_counts = df_validation['Address_Confidence'].value_counts()
        total_addresses = len(df_validation)
        quality_definitions = {
            'ULTRA_HIGH': {'Processing_Type': 'Zero Touch', 'Business_Value': 'Immediate print ready', 'Automation_Level': 'Fully-Auto', 'Routing_Decision': 'Direct Mail'},
            'HIGH': {'Processing_Type': 'Quick Review', 'Business_Value': 'Minimal validation needed', 'Automation_Level': 'Semi-Auto', 'Routing_Decision': 'Direct Mail'},
            'MEDIUM': {'Processing_Type': 'Standard Review', 'Business_Value': 'Normal processing required', 'Automation_Level': 'Manual', 'Routing_Decision': 'Mixed (Direct Mail + Agency)'},
            'LOW': {'Processing_Type': 'Agency Routing', 'Business_Value': 'External investigation required', 'Automation_Level': 'Manual', 'Routing_Decision': 'Agency'}
        }
        quality_levels = ['ULTRA_HIGH', 'HIGH', 'MEDIUM', 'LOW']
        quality_data = []
        percentages = []
        if total_addresses > 0:
            raw_percentages = [(quality_counts.get(level, 0) / total_addresses) * 100 for level in quality_levels]
            for i in range(len(raw_percentages) - 1):
                percentages.append(round(raw_percentages[i], 1))
            last_percentage = 100.0 - sum(percentages)
            percentages.append(round(last_percentage, 1))
        else:
            percentages = [0.0, 0.0, 0.0, 0.0]
        for i, quality_level in enumerate(quality_levels):
            count = quality_counts.get(quality_level, 0)
            quality_info = quality_definitions.get(quality_level, {})
            quality_data.append({
                'Quality_Level': quality_level, 'Count': count, 'Percentage': percentages[i],
                'Processing_Type': quality_info.get('Processing_Type', 'Unknown'),
                'Business_Value': quality_info.get('Business_Value', 'Not defined'),
                'Automation_Level': quality_info.get('Automation_Level', 'Manual'),
                'Routing_Decision': quality_info.get('Routing_Decision', 'Unknown'),
                'CP': campaign_cp,
                'comune': '; '.join(campaign_municipalities) if isinstance(campaign_municipalities, list) else campaign_municipalities,
                'provincia': campaign_provincia
            })
        return pd.DataFrame(quality_data)

    def calculate_executive_kpis(self, enhanced_funnel_df, quality_distribution_df):
        """Calculate executive-level KPIs from enhanced funnel data"""
        land_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Land Acquisition']
        contact_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Contact Processing']
        input_parcels = land_funnel[land_funnel['Stage'] == '1. Input Parcels']['Count'].iloc[0]
        qualified_parcels = land_funnel[land_funnel['Stage'] == '4. Parcels w/ Residential Buildings']['Count'].iloc[0]
        land_efficiency = round((qualified_parcels / input_parcels * 100) if input_parcels > 0 else 0, 1)
        owners = contact_funnel[contact_funnel['Stage'] == '1. Owner Discovery']['Count'].iloc[0]
        addresses = contact_funnel[contact_funnel['Stage'] == '2. Address Expansion']['Count'].iloc[0]
        contact_multiplication = round((addresses / qualified_parcels) if qualified_parcels > 0 else 0, 1)
        direct_mail = contact_funnel[contact_funnel['Stage'] == '4. Direct Mail Ready']['Count'].iloc[0]
        direct_mail_efficiency = round((direct_mail / addresses * 100) if addresses > 0 else 0, 1)
        ultra_high_count = quality_distribution_df[quality_distribution_df['Quality_Level'] == 'ULTRA_HIGH']['Count'].iloc[0] if len(quality_distribution_df) > 0 else 0
        high_count = quality_distribution_df[quality_distribution_df['Quality_Level'] == 'HIGH']['Count'].iloc[0] if len(quality_distribution_df) > 0 else 0
        total_quality_addresses = quality_distribution_df['Count'].sum() if len(quality_distribution_df) > 0 else addresses
        zero_touch_rate = round((ultra_high_count / total_quality_addresses * 100) if total_quality_addresses > 0 else 0, 1)
        high_quality_rate = round(((ultra_high_count + high_count) / total_quality_addresses * 100) if total_quality_addresses > 0 else 0, 1)
        return {
            'land_acquisition_efficiency': land_efficiency, 'contact_multiplication_factor': contact_multiplication,
            'direct_mail_efficiency': direct_mail_efficiency, 'zero_touch_processing_rate': zero_touch_rate,
            'high_quality_processing_rate': high_quality_rate, 'total_input_parcels': input_parcels,
            'qualified_parcels': qualified_parcels, 'total_owners': owners, 'total_addresses': addresses,
            'direct_mail_contacts': direct_mail, 'ultra_high_addresses': ultra_high_count
        }


    def create_owners_by_parcel_sheets(self, df_all_raw):
        """
        Create two sheets for parcel ownership analysis:
        1. Owners_By_Parcel: Wide format (user-friendly)
        2. Owners_Normalized: Normalized format (Power BI ready)
        """
        if df_all_raw.empty:
            self.logger.warning("No raw data available for parcel ownership analysis")
            return pd.DataFrame(), pd.DataFrame()
        
        print(f"   🏠 Creating parcel ownership analysis...")
        
        parcel_groups = df_all_raw.groupby(['comune_input', 'foglio_input', 'particella_input'])
        
        wide_format_data = []
        normalized_data = []
        
        for (comune, foglio, particella), group in parcel_groups:
            cp = group['CP_input'].iloc[0] if 'CP_input' in group.columns else ''
            area = group['Area_input'].iloc[0] if 'Area_input' in group.columns else ''
            
            try:
                parcel_area_ha = float(str(area).replace(',', '.')) if pd.notna(area) and area != '' else 0.0
            except (ValueError, TypeError):
                parcel_area_ha = 0.0
            
            unique_owners = []
            seen_owners = set()
            
            for _, row in group.iterrows():
                cf = row.get('cf_owner', '')
                denominazione = row.get('denominazione_owner', '')
                nome = row.get('nome', '')
                cognome = row.get('cognome', '')
                quota = row.get('quota_owner', 'missing')
                
                if pd.notna(nome) and pd.notna(cognome) and nome and cognome:
                    owner_name = f"{cognome} {nome}".strip()
                elif pd.notna(denominazione):
                    owner_name = str(denominazione).strip()
                else:
                    owner_name = "N/A"
                
                owner_key = f"{cf}_{owner_name}"
                
                if owner_key not in seen_owners and cf and cf != 'N/A':
                    seen_owners.add(owner_key)
                    owner_type = self.classify_owner_type(cf)
                    if pd.isna(quota) or quota == '' or quota == 'N/A':
                        quota = 'missing'
                    unique_owners.append({'name': owner_name, 'cf': cf, 'quota': str(quota), 'type': owner_type})
            
            unique_owners.sort(key=lambda x: x['name'])
            total_owners = len(unique_owners)
            
            wide_row = {'comune': comune, 'CP': cp, 'foglio_input': foglio, 'particella_input': particella, 'parcel_area_ha': parcel_area_ha, 'total_owners': total_owners}
            
            for i in range(10):
                if i < len(unique_owners):
                    owner = unique_owners[i]
                    wide_row[f'owner_{i+1}_name'] = owner['name']
                    wide_row[f'owner_{i+1}_cf'] = owner['cf']
                    wide_row[f'owner_{i+1}_quota'] = owner['quota']
                else:
                    wide_row[f'owner_{i+1}_name'] = ''
                    wide_row[f'owner_{i+1}_cf'] = ''
                    wide_row[f'owner_{i+1}_quota'] = ''
            
            if total_owners > 10:
                additional_count = total_owners - 10
                wide_row['additional_owners'] = f"...and {additional_count} more owners"
                wide_row['ownership_summary'] = f"10 shown + {additional_count} more = {total_owners} total"
            else:
                wide_row['additional_owners'] = ''
                wide_row['ownership_summary'] = f"All {total_owners} owners shown"
            
            wide_format_data.append(wide_row)
            
            for owner in unique_owners:
                normalized_row = {
                    'comune': comune, 'CP': cp, 'foglio_input': foglio, 'particella_input': particella,
                    'parcel_area_ha': parcel_area_ha, 'owner_name': owner['name'], 'owner_cf': owner['cf'],
                    'quota': owner['quota'], 'owner_type': owner['type']
                }
                normalized_data.append(normalized_row)
        
        df_wide = pd.DataFrame(wide_format_data)
        df_normalized = pd.DataFrame(normalized_data)
        
        if not df_wide.empty:
            df_wide = df_wide.sort_values(['comune', 'total_owners', 'foglio_input', 'particella_input'], ascending=[True, False, True, True])
        
        if not df_normalized.empty:
            df_normalized = df_normalized.sort_values(['comune', 'foglio_input', 'particella_input', 'owner_name'])
        
        print(f"   📊 Parcel ownership analysis complete: {len(df_wide)} parcels, {len(df_normalized)} owner-parcel relationships")
        
        return df_wide, df_normalized
    
    def create_campaign_scorecard(self, df_all_validation_ready, df_all_companies):
        """v3.0.0: Creates the Campaign Scorecard summary DataFrame."""
        scorecard_data = []

        if not df_all_validation_ready.empty:
            direct_mail_df = df_all_validation_ready[df_all_validation_ready['Routing_Channel'] == 'DIRECT_MAIL'].copy()
            if not direct_mail_df.empty:
                direct_mail_parcels = direct_mail_df.drop_duplicates(subset=['foglio_input', 'particella_input'])
                scorecard_data.append({
                    'Category': 'Direct Mail Campaign',
                    'Unique People': direct_mail_df['cf_owner'].nunique(),
                    'Mailings Sent': len(direct_mail_df),
                    'Parcels Affected': len(direct_mail_parcels),
                    'Hectares Affected': pd.to_numeric(direct_mail_parcels['Area_input'].astype(str).str.replace(',', '.'), errors='coerce').sum()
                })
            
            agency_df = df_all_validation_ready[df_all_validation_ready['Routing_Channel'] == 'AGENCY'].copy()
            if not agency_df.empty:
                agency_parcels = agency_df.drop_duplicates(subset=['foglio_input', 'particella_input'])
                scorecard_data.append({
                    'Category': 'Agency Review',
                    'Unique People': agency_df['cf_owner'].nunique(),
                    'Mailings Sent': len(agency_df),
                    'Parcels Affected': len(agency_parcels),
                    'Hectares Affected': pd.to_numeric(agency_parcels['Area_input'].astype(str).str.replace(',', '.'), errors='coerce').sum()
                })

        if not df_all_companies.empty:
            company_parcels = df_all_companies.drop_duplicates(subset=['foglio_input', 'particella_input'])
            scorecard_data.append({
                'Category': 'Company Outreach',
                'Unique People': f"{df_all_companies['cf_owner'].nunique()} (Entities)",
                'Mailings Sent': f"{df_all_companies['pec_email'].notna().sum()} (PEC Found)",
                'Parcels Affected': len(company_parcels),
                'Hectares Affected': pd.to_numeric(company_parcels['Area_input'].astype(str).str.replace(',', '.'), errors='coerce').sum()
            })
            
        return pd.DataFrame(scorecard_data)
    
    def create_consolidated_excel_output(self, campaign_name, all_raw_data, all_validation_ready, all_companies_found, all_summaries, all_funnels):
        """v2.9.9: Creates a single, consolidated Excel file with all campaign results."""
        campaign_dir = os.path.join(self.config.get("output_structure", {}).get("completed_campaigns_dir", "completed_campaigns"), campaign_name)
        os.makedirs(campaign_dir, exist_ok=True)
        output_file = os.path.join(campaign_dir, f"{campaign_name}_Results.xlsx")

        print(f"\n📝 Consolidating results into single file: {output_file}")

        # Concatenate all dataframes from the lists
        df_all_raw = pd.concat(all_raw_data, ignore_index=True) if all_raw_data else pd.DataFrame()
        df_all_validation_ready = pd.concat(all_validation_ready, ignore_index=True) if all_validation_ready else pd.DataFrame()
        df_all_companies = pd.concat(all_companies_found, ignore_index=True) if all_companies_found else pd.DataFrame()
        df_campaign_summary = pd.DataFrame(all_summaries) if all_summaries else pd.DataFrame()
        
        # This block is preserved from your original script
        df_all_funnels = pd.DataFrame()
        df_quality_distribution = pd.DataFrame()
        executive_kpis = {}
        if not df_campaign_summary.empty:
            campaign_cp = df_campaign_summary['CP'].iloc[0] if len(df_campaign_summary) > 0 else "Unknown"
            campaign_municipalities = df_campaign_summary['comune'].unique().tolist() if len(df_campaign_summary) > 0 else ["Unknown"]
            campaign_provincia = df_campaign_summary['provincia'].iloc[0] if len(df_campaign_summary) > 0 else "Unknown"
            
            aggregated_summary = {col: df_campaign_summary[col].sum(numeric_only=True) for col in df_campaign_summary.columns}
            aggregated_funnel_metrics = {
                'input_parcels': aggregated_summary.get('Input_Parcels'),
                'input_area_ha': aggregated_summary.get('Input_Area_Ha'),
                'after_api_parcels': aggregated_summary.get('After_API_Parcels'),
                'after_api_area_ha': aggregated_summary.get('After_API_Area_Ha')
            }
            aggregated_municipality = {
                'CP': campaign_cp,
                'comune': '; '.join(campaign_municipalities),
                'provincia': campaign_provincia
            }

            print("✅ Campaign summary available - creating enhanced funnel...")
            try:
                df_all_funnels = self.create_funnel_analysis_df(aggregated_summary, aggregated_funnel_metrics, aggregated_municipality)
                print(f"✅ Enhanced funnel created: {len(df_all_funnels)} rows")
                if not df_all_validation_ready.empty:
                    print("✅ Validation data available - creating quality distribution...")
                    df_quality_distribution = self.create_quality_distribution_df(df_all_validation_ready, campaign_cp, campaign_municipalities, campaign_provincia)
                    print(f"✅ Quality distribution created: {len(df_quality_distribution)} rows")
                else:
                    print("❌ No validation data - skipping quality distribution")

                if not df_all_funnels.empty and not df_quality_distribution.empty:
                    executive_kpis = self.calculate_executive_kpis(df_all_funnels, df_quality_distribution)
            except Exception as e:
                print(f"❌ Enhanced funnel/KPI creation failed: {str(e)}")
                import traceback
                traceback.print_exc()

        # --- Create Additional Analysis & Summary Sheets (Corrected and Integrated) ---
        df_strategic_mailing = pd.DataFrame()
        df_owners_wide = pd.DataFrame()
        df_owners_normalized = pd.DataFrame()
        df_scorecard = pd.DataFrame()
        
        # 1. Create Parcel Ownership Analysis Sheets (uses df_all_raw) - PRESERVED
        if not df_all_raw.empty:
            df_owners_wide, df_owners_normalized = self.create_owners_by_parcel_sheets(df_all_raw)

        # 2. Create Scorecard and Strategic Mailing List (uses df_all_validation_ready)
        if not df_all_validation_ready.empty:
            # Create the Campaign Scorecard - PRESERVED
            df_scorecard = self.create_campaign_scorecard(df_all_validation_ready, df_all_companies)
            
            # --- Create the Strategic Mailing List DataFrame (Corrected Logic) ---
            if 'Parcel_ID' in df_all_validation_ready.columns and 'cf_owner' in df_all_validation_ready.columns:
                high_confidence_contacts = df_all_validation_ready[df_all_validation_ready['Address_Confidence'].isin(['ULTRA_HIGH', 'HIGH', 'MEDIUM'])]
                owner_to_addresses = high_confidence_contacts.groupby('cf_owner')['Best_Address'].unique().apply(list).to_dict()
                
                owners_with_good_address = df_all_validation_ready[df_all_validation_ready['cf_owner'].isin(owner_to_addresses.keys())].copy()
                
                grouped_by_owner = owners_with_good_address.groupby('cf_owner').agg(
                    Full_Name=('denominazione_owner', 'first'),
                    Elenco_Parcel_ID=('Parcel_ID', lambda x: '; '.join(x.unique()))
                ).reset_index()

                output_rows = []
                for _, owner_row in grouped_by_owner.iterrows():
                    cf = owner_row['cf_owner']
                    mailing_addresses = owner_to_addresses.get(cf, [])
                    for address in mailing_addresses:
                        output_rows.append({
                            'Full_Name': owner_row['Full_Name'],
                            'cf': cf,
                            'Mailing_Address': address,
                            'Elenco_Parcel_ID': owner_row['Elenco_Parcel_ID']
                        })
                
                if output_rows:
                    df_strategic_mailing = pd.DataFrame(output_rows)
                    df_strategic_mailing = df_strategic_mailing.sort_values(by=['cf']).reset_index(drop=True)
            else:
                self.logger.warning("Required columns ('Parcel_ID', 'cf_owner') not found in validation_ready data, cannot create mailing list.")

        # --- Write all sheets to the Excel file ---
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            if not df_all_validation_ready.empty:
                df_all_validation_ready.to_excel(writer, sheet_name='All_Validation_Ready', index=False)
            if not df_strategic_mailing.empty:
                df_strategic_mailing.to_excel(writer, sheet_name='Final_Mailing_List', index=False)
            
            if not df_all_companies.empty:
                df_all_companies.to_excel(writer, sheet_name='All_Companies_Found', index=False)
                print(f"   📋 All_Companies_Found: {len(df_all_companies)} company records")
            else:
                empty_companies_df = pd.DataFrame(columns=['CP', 'comune', 'provincia', 'denominazione', 'cf_owner', 'pec_email', 'pec_status'])
                empty_companies_df.to_excel(writer, sheet_name='All_Companies_Found', index=False)
                print(f"   📋 All_Companies_Found: 0 company records (empty sheet created)")

            if not df_campaign_summary.empty:
                df_campaign_summary.to_excel(writer, sheet_name='Campaign_Summary', index=False)
            if not df_all_funnels.empty:
                df_all_funnels.to_excel(writer, sheet_name='Enhanced_Funnel_Analysis', index=False)
                print(f"   📊 Enhanced_Funnel_Analysis: {len(df_all_funnels)} funnel stages")
            if not df_quality_distribution.empty:
                df_quality_distribution.to_excel(writer, sheet_name='Address_Quality_Distribution', index=False)
                print(f"   🎯 Address_Quality_Distribution: Quality analysis")
            if not df_all_raw.empty:
                df_all_raw.to_excel(writer, sheet_name='All_Raw_Data', index=False)
            
            if not df_owners_wide.empty:
                df_owners_wide.to_excel(writer, sheet_name='Owners_By_Parcel', index=False)
                print(f"   🏠 Owners_By_Parcel: {len(df_owners_wide)} parcels analyzed")
            if not df_owners_normalized.empty:
                df_owners_normalized.to_excel(writer, sheet_name='Owners_Normalized', index=False)
                print(f"   📊 Owners_Normalized: {len(df_owners_normalized)} owner-parcel relationships")
            if not df_scorecard.empty:
                df_scorecard.to_excel(writer, sheet_name='Campaign_Scorecard', index=False)
                print(f"   🏆 Campaign_Scorecard: High-level summary created")

        print(f"   ✅ Consolidated output saved: {os.path.basename(output_file)}")
        print(f"   📋 Total sheets: Enhanced with funnel analysis, quality distribution, and ownership analysis")

        if executive_kpis:
            print(f"   🏆 Executive KPIs:")
            print(f"     • Land Acquisition Efficiency: {executive_kpis.get('land_acquisition_efficiency', 0)}%")
            print(f"     • Contact Multiplication Factor: {executive_kpis.get('contact_multiplication_factor', 0)}x")
            print(f"     • Zero-Touch Processing Rate: {executive_kpis.get('zero_touch_processing_rate', 0)}%")
            print(f"     • Direct Mail Efficiency: {executive_kpis.get('direct_mail_efficiency', 0)}%")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Enhanced Land Acquisition Pipeline v2.9')
    parser.add_argument('--config', required=True, help='Campaign configuration file')
    parser.add_argument('--start-balance', type=float, help='Starting API balance')
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r') as f:
            campaign_config = json.load(f)
        pipeline = IntegratedLandAcquisitionPipeline()
        pipeline.run_complete_campaign(campaign_config['input_file'], campaign_config['campaign_name'], args.start_balance)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
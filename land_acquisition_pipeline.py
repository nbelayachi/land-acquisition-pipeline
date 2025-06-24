# -*- coding: utf-8 -*-
"""
Enhanced Land Acquisition Pipeline with Geocoding Integration
Handles complete workflow from single input file to municipality-structured outputs
ENHANCED: Automatic geocoding and PEC email retrieval
VERSION: 2.7 (with v2.6 bugfixes)

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
        """Create Power BI export data with ENHANCED business intelligence metrics"""
        powerbi_data = []
        
        for municipality_key, stats in self.campaign_stats.get('municipalities_processed', {}).items():
            summary_metrics = stats.get("summary_metrics", {})
            municipality_record = {
                "Campaign_Date": datetime.now().strftime("%Y-%m-%d"),
                "Campaign_Name": campaign_name,
                "Municipality_Key": municipality_key,
                "CP": stats.get("CP", municipality_key.split('_')[0]),
                "Municipality": stats.get("comune", '_'.join(municipality_key.split('_')[1:]).replace('_', ' ')),

                "Input_Parcels": summary_metrics.get("Input_Parcels", 0),
                "API_Success_Rate": summary_metrics.get("API_Success_Rate", 0.0),
                "Unique_Individual_Owners": summary_metrics.get("Unique_Individual_Owners", 0),
                "Unique_Company_Owners": summary_metrics.get("Unique_Company_Owners", 0),
                "High_Confidence_Direct_Mail": summary_metrics.get("High_Confidence_Direct_Mail", 0),
                "Agency_Required_Final": summary_metrics.get("Agency_Required_Final", 0),
                "Interpolation_Risks_Detected": summary_metrics.get("Interpolation_Risks_Detected", 0),
                "Category_A_Filter_Rate": summary_metrics.get("Category_A_Filter_Rate", 0.0),
                "Address_Geocoding_Success_Rate": summary_metrics.get("Address_Geocoding_Success_Rate", 0.0),
                "Companies_With_PEC": summary_metrics.get("Companies_With_PEC", 0),
                "PEC_Success_Rate": summary_metrics.get("PEC_Success_Rate", 0.0),
                "Hectares_Direct_Mail": summary_metrics.get("Hectares_Direct_Mail", 0.0),
                "Hectares_Agency_Required": summary_metrics.get("Hectares_Agency_Required", 0.0),

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
            print(f"   📊 Power BI dataset created with enhanced metrics: {os.path.basename(powerbi_file)}")

    def classify_address_quality(self, row):
        """
        Classify address quality based on original vs geocoded comparison.
        """
        original = str(row.get('cleaned_ubicazione', '')).strip()
        geocoded = str(row.get('Geocoded_Address_Italian', '')).strip()
        has_geocoding = row.get('Geocoding_Status') == 'Success'
        
        def extract_street_number(address):
            # --- FIX START: Task 1 - Enhanced regex to capture numbers with suffixes like "32/A" ---
            # New patterns capture digits followed by optional suffixes like /A or B.
            patterns = [
                r'n\.?\s*(\d+[A-Za-z/]{0,2})',  # Handles "n. 32", "n. 32/A", "n.32B"
                r'\b(\d+[A-Za-z/]{0,2})$',      # Handles "32", "32/A" at the end of the string
                r',\s*(\d+[A-Za-z/]{0,2})'      # Handles ", 32", ", 32/A"
            ]
            # --- FIX END ---
            for pattern in patterns:
                match = re.search(pattern, address, re.IGNORECASE)
                if match:
                    # Return the full matched group, converted to uppercase for consistent comparison
                    return match.group(1).upper()
            return None
        
        original_num = extract_street_number(original)
        geocoded_num = extract_street_number(geocoded) if has_geocoding else None
        
        # --- FIX START: Task 1 & 2 - Reordered logic to handle SNC first and fix mismatch detection ---
        # The 'SNC' check is now first to prevent incorrect "interpolation" notes.
        # The number comparison is now exact after converting to uppercase.
        if 'SNC' in original.upper():
            return {'Address_Confidence': 'LOW', 'Interpolation_Risk': False, 'Best_Address': '', 'Routing_Channel': 'AGENCY', 'Quality_Notes': 'SNC (no street number) - requires agency'}
        
        elif original_num and geocoded_num and original_num == geocoded_num:
            return {'Address_Confidence': 'HIGH', 'Interpolation_Risk': False, 'Best_Address': geocoded, 'Routing_Channel': 'DIRECT_MAIL', 'Quality_Notes': 'Complete and verified address'}
        
        elif original_num and geocoded_num and original_num != geocoded_num:
            return {'Address_Confidence': 'MEDIUM', 'Interpolation_Risk': True, 'Best_Address': original, 'Routing_Channel': 'DIRECT_MAIL', 'Quality_Notes': f'Number mismatch. Using original number "{original_num}" instead of geocoded "{geocoded_num}"'}
        
        elif not original_num and geocoded_num:
            return {'Address_Confidence': 'LOW', 'Interpolation_Risk': True, 'Best_Address': '', 'Routing_Channel': 'AGENCY', 'Quality_Notes': f'Number "{geocoded_num}" likely interpolated by geocoding API'}
        
        elif original_num and not geocoded_num:
             return {'Address_Confidence': 'MEDIUM', 'Interpolation_Risk': False, 'Best_Address': original, 'Routing_Channel': 'DIRECT_MAIL', 'Quality_Notes': f'Original address has number "{original_num}", but it could not be verified by geocoding.'}

        else: # No numbers in either source
            return {'Address_Confidence': 'LOW', 'Interpolation_Risk': False, 'Best_Address': '', 'Routing_Channel': 'AGENCY', 'Quality_Notes': 'No street number available in any source'}
        # --- FIX END ---
    
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
- **Smarter Addresses (NEW!)**: Each address now has a quality score (`Address_Confidence`) and a recommended `Routing_Channel` (DIRECT_MAIL or AGENCY) to minimize costs from returned mail.
{pec_summary}- **Smarter Summaries**: The `Municipality_Summary` sheet in the `_Complete_Results.xlsx` file now contains powerful business intelligence metrics.
---

**For the Land Acquisition Team:**

1.  **Primary File**: Go to the campaign folder and open `Validation_Ready.xlsx` in each municipality sub-folder.
2.  **Your Goal**: Identify high-quality prospects for our mailing campaigns.
3.  **Workflow**:
    * This list is now clean and efficient. 
    * **Focus on `Routing_Channel` = 'DIRECT_MAIL'**. These are the highest quality addresses.
    * Use `Address_Confidence` and `Quality_Notes` for more detail.
    {geocoding_summary}

**For the Business Development Team:**

- Please review the `Companies_Found.xlsx` files. They now include a `pec_email` column for direct digital contact with company owners.

**For Management:**

- The `PowerBI_Dataset.csv` has been updated with the new, enhanced business metrics for strategic review.
- The `Enhanced_Cost_Summary.txt` provides a full breakdown of campaign ROI and recovery savings.

**Location:**
`OneDrive > ... > Campaigns > {campaign_name}`

Any questions, please contact [Your Name].

Best,
[Your Name]
        """.strip()
        
        notification_file = os.path.join(onedrive_dir, "README_Team_Instructions.txt")
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(notification_content)

    def create_municipality_summary(self, municipality_key, municipality_data, df_raw, validation_ready, companies_found=None):
        """
        Creates an enhanced municipality summary with high-impact business metrics.
        """
        # --- FIX START: Task 3 - Standardize Area column before calculation ---
        # This ensures that decimal commas (e.g., "2,59") are handled correctly.
        if 'Area' in validation_ready.columns:
            validation_ready['Area'] = pd.to_numeric(validation_ready['Area'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        # --- FIX END ---

        if 'cf' not in df_raw.columns:
            return { "Error": "cf column not found in raw data" }
        df_raw['cf'] = df_raw['cf'].astype(str)

        individual_cfs = df_raw[df_raw['cf'].str[0].str.isalpha()]['cf'].unique()
        company_cfs = df_raw[df_raw['cf'].str[0].str.isdigit()]['cf'].unique()
        
        # --- FIX START: Task 3 - Correct API Success Rate calculation ---
        # The original calculation was flawed. This correctly counts unique processed parcels.
        parcels_with_data = len(df_raw[['foglio_input', 'particella_input']].drop_duplicates())
        # --- FIX END ---
        api_success_rate = (parcels_with_data / municipality_data['parcel_count']) * 100 if municipality_data['parcel_count'] > 0 else 0
        
        individuals_cat_a_raw = df_raw[(df_raw['Tipo_Proprietario'] == 'Privato') & (df_raw['classamento'].str.contains('Cat.A', na=False))]
        category_a_filter_rate = (len(validation_ready) / len(individuals_cat_a_raw)) * 100 if len(individuals_cat_a_raw) > 0 else 0
        
        geocoding_success_count = 0
        if 'Geocoding_Status' in validation_ready.columns:
            geocoding_success_count = len(validation_ready[validation_ready['Geocoding_Status'] == 'Success'])
        address_geocoding_success_rate = (geocoding_success_count / len(validation_ready)) * 100 if len(validation_ready) > 0 else 0

        high_confidence_contacts = 0
        agency_required_contacts = 0
        interpolation_risks = 0
        hectares_direct_mail = 0.0
        hectares_agency_required = 0.0

        if 'Address_Confidence' in validation_ready.columns and 'Area' in validation_ready.columns:
            direct_mail_df = validation_ready[validation_ready['Routing_Channel'] == 'DIRECT_MAIL']
            agency_df = validation_ready[validation_ready['Routing_Channel'] == 'AGENCY']

            high_confidence_contacts = len(direct_mail_df[direct_mail_df['Address_Confidence'] == 'HIGH'])
            agency_required_contacts = len(agency_df)
            interpolation_risks = len(validation_ready[validation_ready['Interpolation_Risk'] == True])
            
            hectares_direct_mail = direct_mail_df['Area'].sum()
            hectares_agency_required = agency_df['Area'].sum()
        
        companies_with_pec = 0
        pec_success_rate = 0.0
        if companies_found is not None and not companies_found.empty and 'pec_status' in companies_found.columns:
            companies_with_pec = len(companies_found[companies_found['pec_status'] == 'found'])
            total_companies_for_pec = len(companies_found)
            if total_companies_for_pec > 0:
                pec_success_rate = (companies_with_pec / total_companies_for_pec) * 100

        return {
            "Input_Parcels": municipality_data['parcel_count'],
            "API_Success_Rate": api_success_rate,
            "Unique_Individual_Owners": len(individual_cfs),
            "Unique_Company_Owners": len(company_cfs),
            "High_Confidence_Direct_Mail": high_confidence_contacts,
            "Agency_Required_Final": agency_required_contacts,
            "Interpolation_Risks_Detected": interpolation_risks,
            "Hectares_Direct_Mail": hectares_direct_mail,
            "Hectares_Agency_Required": hectares_agency_required,
            "Companies_With_PEC": companies_with_pec,
            "PEC_Success_Rate": pec_success_rate,
            "Category_A_Filter_Rate": category_a_filter_rate,
            "Address_Geocoding_Success_Rate": address_geocoding_success_rate
        }
    
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
        self.logger.info("Enhanced Land Acquisition Pipeline initialized")
    
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
                        all_owners_data = [{"denominazione": i.get('denominazione', 'N/A'), "cf": i.get('cf', 'N/A'), "quota": i.get('quota', 'N/A'), "persona_data": None, "recovered": True} for i in immobile.get('intestatari', [])]
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
        """Main method to run the complete integrated campaign."""
        print(f"\n🚀 ENHANCED LAND ACQUISITION CAMPAIGN: {campaign_name}")
        if start_balance is None:
            start_balance = self.get_manual_balance_input("start")
        else:
            self.campaign_stats["start_balance"] = start_balance
        
        try:
            # --- FIX START: Task 3 - Ensure Area is read as string to handle commas ---
            df = pd.read_excel(input_file, dtype={'Area': str})
            # --- FIX END ---
        except Exception as e:
            print(f"❌ Failed to load input file: {e}"); return None
        
        self.analyze_input_structure(df)
        municipality_structure = self.create_municipality_structure(df, campaign_name)
        token = self.config.get("api_settings", {}).get("token", "")
        if not token or token == "YOUR_TOKEN_HERE":
            print("❌ Please update your API token in land_acquisition_config.json"); return None
        
        municipality_results = []
        for municipality_key, municipality_data in municipality_structure.items():
            result = self.process_municipality(municipality_key, municipality_data, token)
            if result:
                municipality_results.append(result)
            self.save_cache()
            if self.geocoding_enabled: self.save_geocoding_cache()
            if self.pec_enabled: self.save_pec_cache()

        if self.campaign_stats["timeout_requests"] > 0:
            self.recover_timeout_requests(token)
        if self.geocoding_enabled and self.campaign_stats["geocoding_timeout_requests"] > 0:
            self.recover_geocoding_timeout_requests()
        
        self.get_manual_balance_input("end")
        campaign_dir = os.path.join(self.config.get("output_structure", {}).get("completed_campaigns_dir", "completed_campaigns"), campaign_name)
        self.create_enhanced_cost_summary(campaign_name, campaign_dir)
        if municipality_results:
            self.create_powerbi_export(campaign_name, campaign_dir)
        self.copy_to_onedrive(campaign_name, campaign_dir)
        
        print(f"\n✅ ENHANCED CAMPAIGN COMPLETED")

    def create_enhanced_cost_summary(self, campaign_name, campaign_dir):
        """Create enhanced cost summary."""
        geocoding_section = f"Geocoding Enabled: {'Yes' if self.geocoding_enabled else 'No'}\n"
        pec_section = f"PEC Integration Enabled: {'Yes' if self.pec_enabled else 'No'}\n"

        cost_summary = f"""
ENHANCED LAND ACQUISITION CAMPAIGN COST SUMMARY
Campaign: {campaign_name}
Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

💰 COST BREAKDOWN:
Start Balance: €{self.campaign_stats['start_balance']:.2f}
End Balance: €{self.campaign_stats['end_balance']:.2f}
Total Campaign Cost: €{self.campaign_stats['campaign_cost']:.2f}

{geocoding_section}{pec_section}
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
        """Process a single municipality through the complete pipeline"""
        print(f"\n🏘️  PROCESSING: {municipality_key} | CP: {municipality_data['CP']} | Parcels: {municipality_data['parcel_count']}")
        df = municipality_data['dataframe']
        raw_results = []
        try:
            for index, row in df.iterrows():
                results = self.get_cadastral_data(row, token)
                if results and not all(r['denominazione'] in ['Timeout', 'No Data'] or 'Error' in r['denominazione'] for r in results):
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
            return None # Stop processing this municipality
        
        print(f"\n   ✅ Completed: {len(df)}/{len(df)} parcels processed")
        if not raw_results:
            print(f"   ⚠️  No results for {municipality_key}"); return None
        return self.create_municipality_output(municipality_key, municipality_data, raw_results)

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

    def create_municipality_output(self, municipality_key, municipality_data, raw_results):
        """Create comprehensive output for a municipality."""
        directory = municipality_data['directory']
        df_raw = pd.DataFrame(raw_results)
        if df_raw.empty:
            print(f"   ⚠️  No raw results for {municipality_key}"); return None
        df_raw['Tipo_Proprietario'] = df_raw['cf'].apply(self.classify_owner_type)
        
        individuals_cat_a = df_raw[(df_raw['Tipo_Proprietario'] == 'Privato') & (df_raw['classamento'].str.contains('Cat.A', na=False, case=False))]
        companies_found = df_raw[(df_raw['Tipo_Proprietario'] == 'Azienda')].copy()
        
        validation_ready = pd.DataFrame()
        if not individuals_cat_a.empty:
            required_cols = ['foglio_input', 'particella_input', 'cognome', 'nome', 'ubicazione', 'cf', 'Area']
            validation_ready = individuals_cat_a[[col for col in required_cols if col in individuals_cat_a.columns]].copy()
            validation_ready = self.clean_addresses_safe(validation_ready)
            if self.geocoding_enabled:
                validation_ready = self.enhance_addresses_with_geocoding(validation_ready)
                classification_results = validation_ready.apply(self.classify_address_quality, axis=1).apply(pd.Series)
                validation_ready = pd.concat([validation_ready, classification_results], axis=1)
            validation_ready.drop_duplicates(subset=['cf', 'cleaned_ubicazione'], inplace=True)
            
        if self.pec_enabled and not companies_found.empty:
            print(f"   📧 Enhancing {len(companies_found)} company records with PEC emails...")
            pec_results = companies_found['cf'].apply(self.get_company_pec)
            companies_found[['pec_email', 'pec_status']] = pec_results.apply(pd.Series)
            time.sleep(self.pec_sleep)

        output_file = os.path.join(directory, f"{municipality_key}_Results.xlsx")
        summary_data = self.create_municipality_summary(municipality_key, municipality_data, df_raw, validation_ready, companies_found)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_raw.to_excel(writer, sheet_name='Raw_Data', index=False)
            if not validation_ready.empty: validation_ready.to_excel(writer, sheet_name='Validation_Ready', index=False)
            if not companies_found.empty: companies_found.to_excel(writer, sheet_name='Companies_Found', index=False)
            pd.DataFrame(list(summary_data.items()), columns=['Metric', 'Value']).to_excel(writer, sheet_name='Municipality_Summary', index=False)
        
        self.campaign_stats["municipalities_processed"][municipality_key] = {
            "CP": municipality_data['CP'], "comune": municipality_data['comune'],
            "summary_metrics": summary_data
        }
        
        print(f"   📁 Output saved: {os.path.basename(output_file)}")
        return {"municipality_key": municipality_key}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Enhanced Land Acquisition Pipeline')
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